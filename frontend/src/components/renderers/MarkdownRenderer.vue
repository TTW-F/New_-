<template>
  <div class="markdown-renderer" v-html="renderedContent"></div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import MarkdownIt from 'markdown-it';
import hljs from 'highlight.js';
import DOMPurify from 'dompurify';
import 'highlight.js/styles/github-dark.css';

interface Props {
  content: string;
}

const props = defineProps<Props>();

const md: MarkdownIt = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: function (str: string, lang: string): string {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return `<pre class="hljs"><code>${hljs.highlight(str, { language: lang, ignoreIllegals: true }).value}</code></pre>`;
      } catch (__) {}
    }
    return `<pre class="hljs"><code>${md.utils.escapeHtml(str)}</code></pre>`;
  }
});

const renderedContent = computed(() => {
  const html = md.render(props.content);
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: [
      'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'ul', 'ol', 'li', 'a', 'code', 'pre', 'blockquote', 'table', 'thead',
      'tbody', 'tr', 'th', 'td', 'span', 'div'
    ],
    ALLOWED_ATTR: ['href', 'class', 'id', 'target', 'rel']
  });
});
</script>

<style scoped lang="scss">
.markdown-renderer {
  :deep(h1), :deep(h2), :deep(h3), :deep(h4), :deep(h5), :deep(h6) {
    margin-top: var(--spacing-lg);
    margin-bottom: var(--spacing-md);
    font-weight: var(--font-semibold);
    line-height: var(--leading-tight);
    
    &:first-child {
      margin-top: 0;
    }
  }
  
  :deep(h1) {
    font-size: var(--text-2xl);
  }
  
  :deep(h2) {
    font-size: var(--text-xl);
  }
  
  :deep(h3) {
    font-size: var(--text-lg);
  }
  
  :deep(p) {
    margin-bottom: var(--spacing-md);
    line-height: var(--leading-relaxed);
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  :deep(ul), :deep(ol) {
    margin-bottom: var(--spacing-md);
    padding-left: var(--spacing-xl);
    
    li {
      margin-bottom: var(--spacing-xs);
      line-height: var(--leading-relaxed);
    }
  }
  
  :deep(a) {
    color: var(--color-primary);
    text-decoration: underline;
    
    &:hover {
      color: var(--color-primary-dark);
    }
  }
  
  :deep(code) {
    font-family: var(--font-mono);
    font-size: 0.9em;
    background-color: var(--color-bg-tertiary);
    padding: 2px 6px;
    border-radius: var(--radius-sm);
  }
  
  :deep(pre) {
    margin-bottom: var(--spacing-md);
    background-color: #1e1e1e;
    padding: var(--spacing-md);
    border-radius: var(--radius-md);
    overflow-x: auto;
    
    code {
      background: none;
      padding: 0;
      color: #d4d4d4;
    }
  }
  
  :deep(blockquote) {
    margin: var(--spacing-md) 0;
    padding-left: var(--spacing-lg);
    border-left: 4px solid var(--color-primary);
    color: var(--color-text-secondary);
    font-style: italic;
  }
  
  :deep(table) {
    width: 100%;
    margin-bottom: var(--spacing-md);
    border-collapse: collapse;
    
    th, td {
      padding: var(--spacing-sm);
      border: 1px solid var(--color-border);
      text-align: left;
    }
    
    th {
      background-color: var(--color-bg-tertiary);
      font-weight: var(--font-semibold);
    }
    
    tr:nth-child(even) {
      background-color: var(--color-bg-secondary);
    }
  }
  
  :deep(strong) {
    font-weight: var(--font-semibold);
  }
  
  :deep(em) {
    font-style: italic;
  }
}
</style>
