# 打字动画优化说明

## 问题描述

用户反馈：AI 回答时出现两个光标（一个竖线光标和一个黑块光标）同时显示。

## 问题原因

在 `AssistantMessage.vue` 中：
```vue
<!-- 旧代码 -->
<span v-if="isStreaming" class="typing-cursor">▊</span>

<style>
.typing-cursor {
  width: 2px;  /* CSS 创建的竖线 */
  height: 1em;
  background-color: var(--color-primary);
}
</style>
```

问题：
1. HTML 中使用了 `▊` 字符（黑块）
2. CSS 又创建了一个 2px 宽的竖线
3. 导致两个光标同时显示

## 解决方案

### 1. 创建专业的打字指示器组件

新建 `TypingIndicator.vue`：
- 使用三个跳动的圆点
- 每个点有不同的动画延迟（0s, 0.2s, 0.4s）
- 形成流畅的波浪效果

```vue
<template>
  <span class="typing-indicator">
    <span class="typing-dot"></span>
    <span class="typing-dot"></span>
    <span class="typing-dot"></span>
  </span>
</template>
```

### 2. 添加跳动动画

在 `animations.scss` 中添加：
```scss
@keyframes typingDot {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.7;
  }
  30% {
    transform: translateY(-8px);
    opacity: 1;
  }
}
```

### 3. 更新相关组件

- **AssistantMessage.vue** - 替换旧光标为 `<TypingIndicator />`
- **MessageList.vue** - 优化 "AI 正在思考" 提示，使用新组件
- **MessageItem.vue** - 移除不再需要的旧光标样式

## 效果对比

### 优化前
- ❌ 两个光标同时显示
- ❌ 视觉混乱
- ❌ 不够现代

### 优化后
- ✅ 单一清晰的动画效果
- ✅ 三个圆点依次跳动
- ✅ 流畅自然的波浪效果
- ✅ 符合现代 UI 设计趋势

## 技术细节

### 动画参数
- **圆点大小**: 6px × 6px
- **圆点间距**: 4px
- **动画时长**: 1.4s
- **缓动函数**: ease-in-out
- **延迟间隔**: 0.2s

### 颜色
- 使用主题色 `var(--color-primary)`
- 支持主题切换

### 性能
- 纯 CSS 动画，GPU 加速
- 无 JavaScript 计算
- 流畅 60fps

## 相关文件

- `frontend/src/components/chat/TypingIndicator.vue` (新建)
- `frontend/src/components/chat/AssistantMessage.vue` (更新)
- `frontend/src/components/chat/MessageList.vue` (更新)
- `frontend/src/components/chat/MessageItem.vue` (更新)
- `frontend/src/assets/styles/animations.scss` (更新)
