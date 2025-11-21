"""
Flask Web应用 - 疲劳监测系统Web界面
功能：提供局域网访问的Web界面，支持：
- 实时视频流显示
- 状态信息展示
- Web端提醒弹窗
- Web端语音播放
"""

from flask import Flask, render_template, Response
from flask_socketio import SocketIO
import cv2
import threading
import time
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from camera.camera_capture import CameraCapture
from detection.face_detector import FaceDetector, LandmarkIndices
from analysis.fatigue_analyzer import FatigueAnalyzer
from analysis.distance_monitor import DistanceMonitor
from analysis.posture_monitor import PostureMonitor
from utils.config_loader import get_config
from alert.alert_manager import AlertManager, AlertType, AlertLevel
from alert.web_alert import WebAlert
from alert.buzzer_alert import BuzzerAlert
from alert.led_alert import LEDAlert

# 初始化Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'fatigue-monitor-secret-key'

# 初始化SocketIO（用于实时通信）
socketio = SocketIO(app, cors_allowed_origins="*")

# 全局变量
monitoring_system = None
video_frame = None
frame_lock = threading.Lock()


class WebMonitoringSystem:
    """Web监测系统类"""

    def __init__(self, config_path: str = "config.yaml"):
        """初始化系统"""
        print("=" * 50)
        print("智能桌面疲劳监测系统 - Web版")
        print("版本: v2.0 (Web Interface)")
        print("=" * 50)

        # 加载配置
        self.config = get_config(config_path)

        # 初始化摄像头
        camera_config = self.config.get_camera_config()
        self.camera = CameraCapture(
            camera_id=0,
            resolution=(
                camera_config['resolution']['width'],
                camera_config['resolution']['height']
            ),
            fps=camera_config['fps'],
            flip=camera_config['flip']
        )

        # 初始化人脸检测器
        face_config = self.config.get_face_detection_config()
        self.face_detector = FaceDetector(
            max_num_faces=face_config['max_num_faces'],
            min_detection_confidence=face_config['min_detection_confidence'],
            min_tracking_confidence=face_config['min_tracking_confidence']
        )

        # 初始化疲劳分析器
        fatigue_config = self.config.get_fatigue_config()
        self.fatigue_analyzer = FatigueAnalyzer(
            ear_threshold=fatigue_config['ear_threshold'],
            perclos_threshold=fatigue_config['perclos_threshold'],
            perclos_window=fatigue_config['perclos_window'],
            blink_min=fatigue_config['blink_min'],
            blink_max=fatigue_config['blink_max'],
            closed_eye_duration=fatigue_config['closed_eye_duration']
        )

        # 初始化距离监测器
        distance_config = self.config.get_distance_config()
        self.distance_monitor = DistanceMonitor(
            warning_distance=distance_config['warning_distance'],
            warning_duration=distance_config['warning_duration'],
            known_face_width=distance_config['known_face_width'],
            focal_length=distance_config['focal_length']
        )

        # 初始化坐姿监测器
        posture_config = self.config.get_posture_config()
        camera_res = camera_config['resolution']
        self.posture_monitor = PostureMonitor(
            pitch_threshold_down=posture_config['pitch_threshold_down'],
            pitch_threshold_up=posture_config['pitch_threshold_up'],
            warning_duration=posture_config['warning_duration'],
            focal_length=distance_config['focal_length'],
            image_width=camera_res['width'],
            image_height=camera_res['height']
        )

        # 初始化提醒系统（Web版）
        alert_config = self.config.get_alert_config()
        self.alert_manager = AlertManager(
            enable_voice=False,  # Web端使用浏览器播放，不使用pyttsx3
            enable_led=alert_config['enable_led'],
            enable_gui=True,  # Web提醒替代GUI
            cooldown_time=alert_config['cooldown_time']
        )

        # 初始化Web提醒器
        self.web_alert = WebAlert(socketio=socketio)
        self.alert_manager.set_gui_alert(self.web_alert)  # 使用web_alert替代gui_alert

        # 初始化蜂鸣器（树莓派本地提醒，模拟模式）
        self.buzzer = BuzzerAlert(pin=18, simulate=True)  # simulate=True使用print模拟

        # 初始化LED（模拟模式）
        if alert_config['enable_led']:
            led_config = self.config.get_led_config()
            led_alert = LEDAlert(
                pin=led_config['pin'],
                blink_duration=led_config['blink_duration']
            )
            self.alert_manager.set_led_alert(led_alert)

        # 运行标志
        self.running = False

        print("\n✓ Web系统初始化完成\n")

    def process_frame(self):
        """处理单帧图像"""
        global video_frame

        ret, frame = self.camera.read()
        if not ret:
            return None

        display_frame = frame.copy()

        # 检测人脸
        detected, face_landmarks_list = self.face_detector.detect(frame)

        if detected and face_landmarks_list:
            face_landmarks = face_landmarks_list[0]
            h, w = frame.shape[:2]

            # 获取关键点数组
            landmarks_array = self.face_detector.get_landmarks_array(face_landmarks, w, h)

            # 绘制人脸网格
            display_frame = self.face_detector.draw_landmarks(display_frame, face_landmarks, draw_contours=True)

            # 提取眼部关键点
            left_eye = landmarks_array[LandmarkIndices.LEFT_EYE]
            right_eye = landmarks_array[LandmarkIndices.RIGHT_EYE]

            # 人脸框
            x_coords = landmarks_array[:, 0]
            y_coords = landmarks_array[:, 1]
            x_min, x_max = int(x_coords.min()), int(x_coords.max())
            y_min, y_max = int(y_coords.min()), int(y_coords.max())

            cv2.rectangle(display_frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

            # 疲劳分析
            fatigue_status = self.fatigue_analyzer.update(left_eye, right_eye)

            # 距离监测
            distance_status = self.distance_monitor.update(
                face_box_width=(x_max - x_min),
                left_eye_landmarks=left_eye,
                right_eye_landmarks=right_eye
            )

            # 坐姿监测
            posture_status = self.posture_monitor.update(landmarks_array)

            # 触发提醒
            self._check_and_trigger_alerts(fatigue_status, distance_status, posture_status)

            # 发送状态更新到Web
            self._send_status_update(fatigue_status, distance_status, posture_status)

            # 绘制分析信息
            self._draw_info(display_frame, fatigue_status, distance_status, posture_status)

        else:
            cv2.putText(display_frame, "No Face Detected", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # 显示FPS
        fps_text = f"FPS: {self.camera.get_fps():.1f}"
        cv2.putText(display_frame, fps_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # 更新全局帧
        with frame_lock:
            video_frame = display_frame.copy()

        return display_frame

    def _check_and_trigger_alerts(self, fatigue_status, distance_status, posture_status):
        """检查并触发提醒"""
        # 严重疲劳（最高优先级，同时触发Web提醒和蜂鸣器）
        if fatigue_status['fatigue_level'] == 3:
            self.alert_manager.trigger_alert(
                AlertType.SEVERE_FATIGUE,
                "Severe fatigue detected! Please rest immediately.",
                AlertLevel.CRITICAL
            )
            # 蜂鸣器本地提醒
            threading.Thread(target=self.buzzer.speak_alert, args=('severe',), daemon=True).start()
            return

        # 一般疲劳
        if fatigue_status['fatigue_level'] >= 1:
            self.alert_manager.trigger_alert(
                AlertType.FATIGUE,
                f"{fatigue_status['fatigue_description']}. Please take a break.",
                AlertLevel.WARNING
            )
            threading.Thread(target=self.buzzer.speak_alert, args=('fatigue',), daemon=True).start()

        # 距离过近
        if distance_status['is_too_close']:
            self.alert_manager.trigger_alert(
                AlertType.DISTANCE,
                "You are too close to the screen. Please move back.",
                AlertLevel.WARNING
            )
            threading.Thread(target=self.buzzer.speak_alert, args=('distance',), daemon=True).start()

        # 坐姿不良
        if posture_status['is_bad_posture']:
            self.alert_manager.trigger_alert(
                AlertType.POSTURE,
                f"Poor posture: {posture_status['posture_type']}. Please adjust.",
                AlertLevel.WARNING
            )
            threading.Thread(target=self.buzzer.speak_alert, args=('posture',), daemon=True).start()

    def _send_status_update(self, fatigue_status, distance_status, posture_status):
        """发送状态更新到Web"""
        status_data = {
            'fatigue': {
                'level': fatigue_status['fatigue_level'],
                'description': fatigue_status['fatigue_description'],
                'ear': round(fatigue_status['ear'], 3),
                'perclos': round(fatigue_status['perclos'] * 100, 1),
                'blink_rate': fatigue_status['blinks_per_minute']
            },
            'distance': {
                'value': round(distance_status['distance'], 1),
                'is_too_close': distance_status['is_too_close']
            },
            'posture': {
                'pitch': round(posture_status['pitch'], 1),
                'yaw': round(posture_status['yaw'], 1),
                'roll': round(posture_status['roll'], 1),
                'type': posture_status['posture_type'],
                'is_bad': posture_status['is_bad_posture']
            }
        }
        self.web_alert.send_status_update(status_data)

    def _draw_info(self, frame, fatigue_status, distance_status, posture_status):
        """在画面上绘制信息"""
        h, w = frame.shape[:2]
        y_offset = 60

        # 疲劳状态
        fatigue_color = (0, 255, 0) if fatigue_status['fatigue_level'] == 0 else \
                       (0, 255, 255) if fatigue_status['fatigue_level'] == 1 else \
                       (0, 165, 255) if fatigue_status['fatigue_level'] == 2 else (0, 0, 255)

        cv2.putText(frame, f"Status: {fatigue_status['fatigue_description']}", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, fatigue_color, 2)

        # 距离
        y_offset += 30
        dist_color = (0, 0, 255) if distance_status['is_too_close'] else (0, 255, 0)
        cv2.putText(frame, f"Distance: {distance_status['distance']:.1f} cm", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, dist_color, 2)

        # 坐姿
        y_offset += 30
        posture_color = (0, 0, 255) if posture_status['is_bad_posture'] else (0, 255, 0)
        cv2.putText(frame, f"Posture: {posture_status['posture_type']}", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, posture_color, 2)

    def start(self):
        """启动监测"""
        if not self.camera.start():
            print("✗ 摄像头启动失败！")
            return False
        self.running = True
        print("✓ 监测系统已启动")
        return True

    def stop(self):
        """停止监测"""
        self.running = False
        self.camera.release()
        self.face_detector.close()
        self.alert_manager.cleanup()
        self.buzzer.cleanup()
        print("✓ 监测系统已停止")


def generate_frames():
    """视频流生成器"""
    while monitoring_system and monitoring_system.running:
        frame = monitoring_system.process_frame()
        if frame is not None:
            # 编码为JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.03)  # ~30 FPS


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    """视频流路由"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')


@socketio.on('connect')
def handle_connect():
    """客户端连接"""
    print('✓ Web客户端已连接')


@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开"""
    print('✗ Web客户端已断开')


def main():
    """主函数"""
    global monitoring_system

    # 初始化监测系统
    monitoring_system = WebMonitoringSystem()

    # 启动监测
    if not monitoring_system.start():
        return

    # 启动Flask服务器
    print("\n" + "=" * 50)
    print("Web服务器启动中...")
    print("请在浏览器中访问: http://0.0.0.0:5000")
    print("局域网访问: http://<树莓派IP>:5000")
    print("按 Ctrl+C 停止服务器")
    print("=" * 50 + "\n")

    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n\n用户中断服务器")
    finally:
        if monitoring_system:
            monitoring_system.stop()


if __name__ == '__main__':
    main()
