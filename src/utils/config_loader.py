"""
配置加载工具
功能：加载和管理config.yaml配置文件
"""

import yaml
import os
from typing import Dict, Any


class ConfigLoader:
    """配置加载器类"""

    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化配置加载器

        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        从YAML文件加载配置

        Returns:
            配置字典
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        print(f"✓ 配置文件加载成功: {self.config_path}")
        return config

    def get(self, key_path: str, default=None):
        """
        获取配置值（支持多层级访问）

        Args:
            key_path: 配置键路径，用.分隔，如 "camera.resolution.width"
            default: 默认值

        Returns:
            配置值

        Example:
            >>> config = ConfigLoader()
            >>> width = config.get("camera.resolution.width")
            >>> print(width)  # 640
        """
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def get_camera_config(self) -> Dict[str, Any]:
        """获取摄像头配置"""
        return self.config.get('camera', {})

    def get_face_detection_config(self) -> Dict[str, Any]:
        """获取人脸检测配置"""
        return self.config.get('face_detection', {})

    def get_fatigue_config(self) -> Dict[str, Any]:
        """获取疲劳检测配置"""
        return self.config.get('fatigue', {})

    def get_distance_config(self) -> Dict[str, Any]:
        """获取距离监测配置"""
        return self.config.get('distance', {})

    def get_posture_config(self) -> Dict[str, Any]:
        """获取坐姿监测配置"""
        return self.config.get('posture', {})

    def get_alert_config(self) -> Dict[str, Any]:
        """获取提醒配置"""
        return self.config.get('alert', {})

    def get_performance_config(self) -> Dict[str, Any]:
        """获取性能配置"""
        return self.config.get('performance', {})


# 全局配置实例（单例模式）
_config_instance = None

def get_config(config_path: str = "config.yaml") -> ConfigLoader:
    """
    获取配置实例（单例）

    Args:
        config_path: 配置文件路径

    Returns:
        ConfigLoader实例
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigLoader(config_path)
    return _config_instance


if __name__ == "__main__":
    # 测试代码
    config = get_config()

    print("\n=== 配置测试 ===")
    print(f"摄像头分辨率: {config.get('camera.resolution.width')}x{config.get('camera.resolution.height')}")
    print(f"EAR阈值: {config.get('fatigue.ear_threshold')}")
    print(f"警告距离: {config.get('distance.warning_distance')} cm")
    print(f"低头阈值: {config.get('posture.pitch_threshold_down')}°")
    print(f"启用语音提醒: {config.get('alert.enable_voice')}")
