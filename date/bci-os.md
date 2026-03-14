# 神经接口操作系统v2.0 开源发布

**作者：Nova Chen**  
**日期：2026.03.05**  
**分类：BIOHACK**

经过六个月的开发，**BCI-OS v2.0** 正式开源！这是一个模块化的脑机接口软件框架，支持主流消费级头戴设备（如OpenBCI、NeuroSky）和高密度科研设备。

## 新特性
- **意念打字模块**：基于稳态视觉诱发电位（SSVEP）和运动想象（MI）混合范式，打字速度可达40字符/分钟。
- **无人机群控制**：通过想象左右手动作控制无人机编队方向，延迟<100ms。
- **插件系统**：支持Python/C++插件，可自定义信号处理流水线。
- **数据集**：包含10小时的多模态脑电数据（已脱敏），用于算法验证。

## 快速开始
```bash
git clone https://github.com/TussalZeus18028/BCI-OS.git
cd BCI-OS
pip install -r requirements.txt
python examples/typing_demo.py