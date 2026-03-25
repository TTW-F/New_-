# Design Document: Tool Result Rendering

## Overview

本设计文档描述智能医疗问答系统中工具调用结果的可读性渲染方案。当前系统将工具返回的JSON数据直接显示，用户难以阅读。本方案通过实现专门的结果渲染器，将不同类型工具的JSON结果转换为结构化、易读的HTML格式。

核心设计理念：
- **类型感知**：根据工具类型选择对应的渲染器
- **结构化展示**：将JSON数据转换为语义化的HTML结构
- **优雅降级**：未知工具类型使用格式化JSON显示
- **交互友好**：支持折叠/展开，减少视觉干扰

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Tool Result Rendering                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  ToolResultRenderer                  │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │              renderToolResult()               │   │   │
│  │  │  - 解析工具类型                               │   │   │
│  │  │  - 选择对应渲染器                             │   │   │
│  │  │  - 返回 HTML 字符串                           │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Specialized Renderers                   │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│  │  │ Symptom  │  │ Disease  │  │  Fuzzy   │          │   │
│  │  │ Renderer │  │ Renderer │  │ Renderer │          │   │
│  │  └──────────┘  └──────────┘  └──────────┘          │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│  │  │  Drug    │  │Treatment │  │ Fallback │          │   │
│  │  │ Renderer │  │ Renderer │  │ Renderer │          │   │
│  │  └──────────┘  └──────────┘  └──────────┘          │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. ToolResultRenderer 主接口

```javascript
/**
 * 工具结果渲染器
 * 根据工具类型将 JSON 结果转换为可读 HTML
 */
const ToolResultRenderer = {
    /**
     * 渲染工具结果
     * @param {string} toolName - 工具名称
     * @param {string|object} result - 工具返回结果
     * @returns {string} HTML 字符串
     */
    render(toolName, result) {
        // 解析结果
        const data = this.parseResult(result);
        
        // 根据工具类型选择渲染器
        switch (toolName) {
            case 'diagnose_by_symptoms':
                return this.renderSymptomDiagnosis(data);
            case 'search_disease_info':
                return this.renderDiseaseInfo(data);
            case 'get_treatment_plan':
                return this.renderTreatmentPlan(data);
            case 'search_drugs':
                return this.renderDrugSearch(data);
            case 'fuzzy_search':
                return this.renderFuzzySearch(data);
            default:
                return this.renderFallback(data);
        }
    },
    
    /**
     * 解析结果为对象
     */
    parseResult(result) {
        if (!result) return null;
        if (typeof result === 'object') return result;
        try {
            return JSON.parse(result);
        } catch (e) {
            return { _raw: result };
        }
    }
};
```

### 2. 症状诊断渲染器

```javascript
/**
 * 渲染症状诊断结果
 * 输入数据格式:
 * {
 *   "input_symptoms": ["感冒", "发烧"],
 *   "possible_diseases": [
 *     {"name": "病毒性肠炎", "description": "...", "match_score": 0.8, "matched_symptoms": 1}
 *   ],
 *   "count": 1
 * }
 */
renderSymptomDiagnosis(data) {
    if (!data || data.error) {
        return this.renderError(data?.error || '诊断失败');
    }
    
    const symptoms = data.input_symptoms || [];
    const diseases = data.possible_diseases || [];
    
    if (diseases.length === 0) {
        return `<div class="tool-result-empty">未找到匹配疾病</div>`;
    }
    
    return `
        <div class="tool-result-diagnosis">
            <div class="result-section">
                <div class="section-title">输入症状</div>
                <div class="symptom-tags">
                    ${symptoms.map(s => `<span class="tag tag-symptom">${this.escapeHtml(s)}</span>`).join('')}
                </div>
            </div>
            <div class="result-section">
                <div class="section-title">可能的疾病 (${diseases.length})</div>
                <div class="disease-list">
                    ${diseases.map(d => this.renderDiseaseItem(d)).join('')}
                </div>
            </div>
        </div>
    `;
}

renderDiseaseItem(disease) {
    const score = disease.match_score || 0;
    const scorePercent = Math.round(score * 100);
    const scoreClass = scorePercent >= 70 ? 'high' : scorePercent >= 40 ? 'medium' : 'low';
    
    return `
        <div class="disease-item">
            <div class="disease-header">
                <span class="disease-name">${this.escapeHtml(disease.name)}</span>
                <span class="match-score ${scoreClass}">${scorePercent}% 匹配</span>
            </div>
            ${disease.description ? `<div class="disease-desc">${this.truncate(disease.description, 100)}</div>` : ''}
            ${disease.matched_symptoms ? `<div class="matched-count">匹配 ${disease.matched_symptoms} 个症状</div>` : ''}
        </div>
    `;
}
```

### 3. 疾病信息渲染器

```javascript
/**
 * 渲染疾病详细信息
 * 输入数据格式:
 * {
 *   "name": "感冒",
 *   "description": "...",
 *   "medical_insurance": "是",
 *   "infection_rate": "...",
 *   "susceptible_population": "...",
 *   "cure_rate": "..."
 * }
 */
renderDiseaseInfo(data) {
    if (!data || data.error) {
        return `<div class="tool-result-empty">未找到该疾病信息</div>`;
    }
    
    return `
        <div class="tool-result-disease">
            <div class="disease-title">${this.escapeHtml(data.name)}</div>
            ${data.description ? `<div class="disease-description">${this.escapeHtml(data.description)}</div>` : ''}
            <div class="disease-meta">
                ${data.medical_insurance ? `<span class="meta-item"><span class="meta-label">医保:</span> ${data.medical_insurance}</span>` : ''}
                ${data.cure_rate ? `<span class="meta-item"><span class="meta-label">治愈率:</span> ${data.cure_rate}</span>` : ''}
                ${data.susceptible_population ? `<span class="meta-item"><span class="meta-label">易感人群:</span> ${data.susceptible_population}</span>` : ''}
            </div>
        </div>
    `;
}
```

### 4. 模糊搜索渲染器

```javascript
/**
 * 渲染模糊搜索结果
 * 输入数据格式:
 * {
 *   "keyword": "感冒",
 *   "entity_type": "Disease",
 *   "results": [
 *     {"name": "人禽流行性感冒", "description": "...", "type": "Disease"}
 *   ],
 *   "count": 3
 * }
 */
renderFuzzySearch(data) {
    if (!data) return this.renderError('搜索失败');
    
    const results = data.results || [];
    
    if (results.length === 0) {
        return `<div class="tool-result-empty">未找到相关结果</div>`;
    }
    
    return `
        <div class="tool-result-search">
            <div class="search-header">
                <span class="search-keyword">搜索: "${this.escapeHtml(data.keyword)}"</span>
                <span class="search-type">${data.entity_type || '全部'}</span>
                <span class="search-count">${results.length} 个结果</span>
            </div>
            <div class="search-results">
                ${results.map(r => this.renderSearchItem(r)).join('')}
            </div>
        </div>
    `;
}

renderSearchItem(item) {
    const typeClass = (item.type || '').toLowerCase();
    return `
        <div class="search-item">
            <div class="item-header">
                <span class="item-name">${this.escapeHtml(item.name)}</span>
                <span class="item-type ${typeClass}">${item.type || '未知'}</span>
            </div>
            ${item.description ? `<div class="item-desc">${this.truncate(item.description, 80)}</div>` : ''}
        </div>
    `;
}
```

### 5. 药品搜索渲染器

```javascript
/**
 * 渲染药品搜索结果
 * 输入数据格式:
 * {
 *   "disease": "感冒",
 *   "drugs": [
 *     {"name": "感冒灵", "usage": "...", "dosage": "..."}
 *   ],
 *   "count": 2
 * }
 */
renderDrugSearch(data) {
    if (!data) return this.renderError('查询失败');
    
    const drugs = data.drugs || [];
    
    if (drugs.length === 0) {
        return `<div class="tool-result-empty">未找到该药品信息</div>`;
    }
    
    return `
        <div class="tool-result-drugs">
            <div class="drugs-header">
                <span class="drugs-disease">${this.escapeHtml(data.disease)} 推荐用药</span>
                <span class="drugs-count">${drugs.length} 种</span>
            </div>
            <div class="drugs-list">
                ${drugs.map(d => this.renderDrugItem(d)).join('')}
            </div>
        </div>
    `;
}

renderDrugItem(drug) {
    return `
        <div class="drug-item">
            <div class="drug-name">${this.escapeHtml(drug.name)}</div>
            ${drug.usage ? `<div class="drug-usage"><span class="label">用法:</span> ${this.escapeHtml(drug.usage)}</div>` : ''}
            ${drug.dosage ? `<div class="drug-dosage"><span class="label">用量:</span> ${this.escapeHtml(drug.dosage)}</div>` : ''}
        </div>
    `;
}
```

### 6. 治疗方案渲染器

```javascript
/**
 * 渲染治疗方案
 * 输入数据格式:
 * {
 *   "disease": "感冒",
 *   "symptoms": [...],
 *   "drugs": [...],
 *   "checks": [...],
 *   "departments": [...],
 *   "diet_suggestions": {...}
 * }
 */
renderTreatmentPlan(data) {
    if (!data || data.error) {
        return `<div class="tool-result-empty">未找到治疗方案</div>`;
    }
    
    const sections = [];
    
    if (data.symptoms?.length) {
        sections.push(`
            <div class="plan-section">
                <div class="section-title">相关症状</div>
                <div class="tag-list">
                    ${data.symptoms.map(s => `<span class="tag tag-symptom">${this.escapeHtml(s)}</span>`).join('')}
                </div>
            </div>
        `);
    }
    
    if (data.drugs?.length) {
        sections.push(`
            <div class="plan-section">
                <div class="section-title">推荐药物</div>
                <div class="tag-list">
                    ${data.drugs.map(d => `<span class="tag tag-drug">${this.escapeHtml(d)}</span>`).join('')}
                </div>
            </div>
        `);
    }
    
    if (data.departments?.length) {
        sections.push(`
            <div class="plan-section">
                <div class="section-title">就诊科室</div>
                <div class="tag-list">
                    ${data.departments.map(d => `<span class="tag tag-dept">${this.escapeHtml(d)}</span>`).join('')}
                </div>
            </div>
        `);
    }
    
    if (data.checks?.length) {
        sections.push(`
            <div class="plan-section">
                <div class="section-title">检查项目</div>
                <div class="tag-list">
                    ${data.checks.map(c => `<span class="tag tag-check">${this.escapeHtml(c)}</span>`).join('')}
                </div>
            </div>
        `);
    }
    
    return `<div class="tool-result-treatment">${sections.join('')}</div>`;
}
```

### 7. 降级渲染器

```javascript
/**
 * 降级渲染 - 格式化 JSON 显示
 */
renderFallback(data) {
    if (!data) return '<div class="tool-result-empty">无结果</div>';
    
    // 如果是原始文本（解析失败）
    if (data._raw) {
        return `<pre class="tool-result-raw">${this.escapeHtml(data._raw)}</pre>`;
    }
    
    // 格式化 JSON
    const json = JSON.stringify(data, null, 2);
    const isLong = json.length > 500;
    
    return `
        <div class="tool-result-json ${isLong ? 'collapsible' : ''}">
            <pre class="json-content">${this.escapeHtml(json)}</pre>
        </div>
    `;
}
```

### 8. 工具函数

```javascript
/**
 * HTML 转义
 */
escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * 文本截断
 */
truncate(text, maxLength) {
    if (!text) return '';
    if (text.length <= maxLength) return this.escapeHtml(text);
    return this.escapeHtml(text.substring(0, maxLength)) + '...';
}

/**
 * 渲染错误信息
 */
renderError(message) {
    return `<div class="tool-result-error">${this.escapeHtml(message)}</div>`;
}
```

## Data Models

### 工具结果数据结构

```typescript
// 症状诊断结果
interface SymptomDiagnosisResult {
    input_symptoms: string[];
    possible_diseases: {
        name: string;
        description?: string;
        match_score: number;
        matched_symptoms?: number;
    }[];
    count: number;
    error?: string;
}

// 疾病信息结果
interface DiseaseInfoResult {
    name: string;
    description?: string;
    medical_insurance?: string;
    infection_rate?: string;
    susceptible_population?: string;
    cure_rate?: string;
    error?: string;
}

// 模糊搜索结果
interface FuzzySearchResult {
    keyword: string;
    entity_type: string;
    results: {
        name: string;
        type: string;
        description?: string;
    }[];
    count: number;
}

// 药品搜索结果
interface DrugSearchResult {
    disease: string;
    drugs: {
        name: string;
        usage?: string;
        dosage?: string;
    }[];
    count: number;
    message?: string;
}

// 治疗方案结果
interface TreatmentPlanResult {
    disease: string;
    symptoms?: string[];
    drugs?: string[];
    checks?: string[];
    departments?: string[];
    diet_suggestions?: object;
    error?: string;
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Symptom Diagnosis Field Presence

*For any* valid symptom diagnosis result containing input_symptoms and possible_diseases, the rendered HTML SHALL contain all input symptom names and all disease names with their match scores.

**Validates: Requirements 1.1, 1.2**

### Property 2: Disease Info Field Presence

*For any* valid disease info result containing name and description, the rendered HTML SHALL contain the disease name and description text.

**Validates: Requirements 2.1, 2.2**

### Property 3: Fuzzy Search Field Presence

*For any* valid fuzzy search result containing keyword, entity_type, and results array, the rendered HTML SHALL contain the search keyword, entity type, and all result item names.

**Validates: Requirements 3.1, 3.2**

### Property 4: Drug Search Field Presence

*For any* valid drug search result containing disease name and drugs array, the rendered HTML SHALL contain the disease name and all drug names.

**Validates: Requirements 4.1, 4.2**

### Property 5: Description Truncation

*For any* description text longer than the maximum length, the rendered output SHALL be shorter than the original and end with ellipsis ("...").

**Validates: Requirements 3.3**

### Property 6: Unknown Tool Fallback

*For any* unknown tool type with valid JSON result, the rendered HTML SHALL contain a formatted JSON representation of the data.

**Validates: Requirements 5.1**

### Property 7: Invalid JSON Fallback

*For any* result that cannot be parsed as JSON, the rendered HTML SHALL contain the raw text content.

**Validates: Requirements 5.4**

## Error Handling

| 场景 | 处理方式 | 显示内容 |
|-----|---------|---------|
| 结果为空 | 显示空状态 | "无结果" |
| JSON 解析失败 | 显示原始文本 | 原始文本内容 |
| 工具返回错误 | 显示错误信息 | 错误消息 |
| 未知工具类型 | 格式化 JSON | 格式化的 JSON |
| 字段缺失 | 跳过该字段 | 不显示该部分 |

## Testing Strategy

### 单元测试

使用 Jest 进行单元测试：

1. **渲染器选择测试**
   - 验证不同工具名称选择正确的渲染器
   - 验证未知工具使用降级渲染器

2. **字段渲染测试**
   - 验证各类型结果的必要字段都被渲染
   - 验证空字段不会导致错误

3. **边界条件测试**
   - 空结果处理
   - 超长文本截断
   - 特殊字符转义

### 属性测试 (Property-Based Testing)

使用 `fast-check` 库进行属性测试：

1. **Property 1-4**: 字段存在性测试
   - 生成随机有效数据，验证渲染结果包含所有必要字段

2. **Property 5**: 截断测试
   - 生成随机长文本，验证截断行为

3. **Property 6-7**: 降级测试
   - 生成随机 JSON 和非 JSON 数据，验证降级行为

### 测试配置

- 每个属性测试运行 100 次迭代
- 使用 `fast-check` 的 `fc.record` 生成结构化测试数据

## CSS Styles

```css
/* 工具结果通用样式 */
.tool-result-diagnosis,
.tool-result-disease,
.tool-result-search,
.tool-result-drugs,
.tool-result-treatment {
    font-size: 13px;
    line-height: 1.5;
}

.result-section,
.plan-section {
    margin-bottom: 12px;
}

.section-title {
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 8px;
    font-size: 12px;
}

/* 标签样式 */
.tag {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
    margin: 2px 4px 2px 0;
}

.tag-symptom {
    background: rgba(59, 130, 246, 0.1);
    color: #3b82f6;
}

.tag-drug {
    background: rgba(16, 185, 129, 0.1);
    color: #10b981;
}

.tag-dept {
    background: rgba(139, 92, 246, 0.1);
    color: #8b5cf6;
}

.tag-check {
    background: rgba(245, 158, 11, 0.1);
    color: #f59e0b;
}

/* 疾病列表 */
.disease-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.disease-item {
    padding: 8px 12px;
    background: var(--bg-secondary);
    border-radius: 6px;
}

.disease-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;
}

.disease-name {
    font-weight: 600;
    color: var(--text-primary);
}

.match-score {
    font-size: 11px;
    padding: 2px 6px;
    border-radius: 4px;
}

.match-score.high {
    background: rgba(16, 185, 129, 0.1);
    color: #10b981;
}

.match-score.medium {
    background: rgba(245, 158, 11, 0.1);
    color: #f59e0b;
}

.match-score.low {
    background: rgba(239, 68, 68, 0.1);
    color: #ef4444;
}

.disease-desc {
    font-size: 12px;
    color: var(--text-secondary);
}

/* 搜索结果 */
.search-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    flex-wrap: wrap;
}

.search-keyword {
    font-weight: 600;
}

.search-type,
.search-count {
    font-size: 11px;
    color: var(--text-secondary);
}

.search-results {
    display: flex;
    flex-direction: column;
    gap: 6px;
    max-height: 200px;
    overflow-y: auto;
}

.search-item {
    padding: 6px 10px;
    background: var(--bg-secondary);
    border-radius: 4px;
}

.item-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.item-name {
    font-weight: 500;
}

.item-type {
    font-size: 10px;
    padding: 1px 4px;
    border-radius: 2px;
    background: var(--bg-tertiary);
}

.item-desc {
    font-size: 11px;
    color: var(--text-secondary);
    margin-top: 2px;
}

/* 空状态和错误 */
.tool-result-empty,
.tool-result-error {
    padding: 12px;
    text-align: center;
    color: var(--text-secondary);
    font-size: 12px;
}

.tool-result-error {
    color: var(--clinical-red);
}

/* JSON 降级显示 */
.tool-result-json pre,
.tool-result-raw {
    font-family: 'Monaco', 'Menlo', monospace;
    font-size: 11px;
    background: var(--bg-secondary);
    padding: 8px;
    border-radius: 4px;
    overflow-x: auto;
    white-space: pre-wrap;
    word-break: break-all;
}

/* 药品列表 */
.drugs-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
}

.drugs-disease {
    font-weight: 600;
}

.drugs-count {
    font-size: 11px;
    color: var(--text-secondary);
}

.drugs-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.drug-item {
    padding: 6px 10px;
    background: var(--bg-secondary);
    border-radius: 4px;
}

.drug-name {
    font-weight: 500;
    margin-bottom: 4px;
}

.drug-usage,
.drug-dosage {
    font-size: 11px;
    color: var(--text-secondary);
}

.drug-usage .label,
.drug-dosage .label {
    color: var(--text-tertiary);
}
```

## Implementation Notes

### 文件修改清单

```
frontend/
├── app.js           # 添加 ToolResultRenderer 对象，修改 formatToolResult 函数
└── styles.css       # 添加工具结果渲染样式
```

### 集成方式

在 `app.js` 中替换现有的 `formatToolResult` 函数：

```javascript
// 原来的实现
const formatToolResult = (result) => {
    if (!result) return '无结果';
    if (typeof result === 'object') {
        return JSON.stringify(result, null, 2);
    }
    // ...
};

// 新的实现
const formatToolResult = (toolName, result) => {
    return ToolResultRenderer.render(toolName, result);
};
```

在模板中修改工具结果显示：

```html
<!-- 原来 -->
<pre class="tool-result-text">{{ formatToolResult(tool.result) }}</pre>

<!-- 新的 -->
<div class="tool-result-content" v-html="formatToolResult(tool.name, tool.result)"></div>
```
