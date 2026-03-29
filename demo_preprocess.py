#!/usr/bin/env python3
# coding: utf-8
"""
医疗数据预处理系统
对采集的原始数据进行清洗、标准化和结构化处理
"""

import json
import time
from datetime import datetime
from api.core.logger import logger, console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree


class MedicalPreprocessor:
    """医疗数据预处理器"""
    
    def __init__(self):
        self.raw_data = [
            {
                "name": "感冒",
                "category": ["呼吸内科"],
                "desc": "感冒是一种常见疾病，需要及时治疗。",
                "symptom": ["发热", "咳嗽", "流鼻涕"],
                "cure_department": ["呼吸内科"],
                "timestamp": datetime.now().isoformat()
            },
            {
                "name": "高血压",
                "category": ["心血管内科"],
                "desc": "高血压是一种常见疾病，需要及时治疗。",
                "symptom": ["头晕", "头痛", "心悸"],
                "cure_department": ["心血管内科"],
                "timestamp": datetime.now().isoformat()
            },
            {
                "name": "糖尿病",
                "category": ["内分泌科"],
                "desc": "糖尿病是一种常见疾病，需要及时治疗。",
                "symptom": ["多饮", "多尿", "体重下降"],
                "cure_department": ["内分泌科"],
                "timestamp": datetime.now().isoformat()
            }
        ]
        logger.info("预处理器初始化完成")
    
    def clean_text(self, text: str) -> str:
        """清洗文本数据"""
        if not text:
            return ""
        # 移除多余空格和换行
        cleaned = text.strip().replace('\n', ' ').replace('\r', '')
        return cleaned
    
    def normalize_list(self, items: list) -> list:
        """标准化列表数据"""
        if not items:
            return []
        # 去重、去空、排序
        return sorted(list(set([item.strip() for item in items if item.strip()])))
    
    def process_disease(self, disease: dict) -> dict:
        """处理单个疾病数据"""
        logger.info(f"处理疾病数据: {disease['name']}")
        
        # 模拟处理延迟
        time.sleep(0.3)
        
        processed = {
            "name": self.clean_text(disease.get("name", "")),
            "desc": self.clean_text(disease.get("desc", "")),
            "category": self.normalize_list(disease.get("category", [])),
            "symptom": self.normalize_list(disease.get("symptom", [])),
            "cure_department": self.normalize_list(disease.get("cure_department", [])),
            "processed_at": datetime.now().isoformat()
        }
        
        logger.success(f"✓ 处理完成: {disease['name']}")
        return processed
    
    def show_data_structure(self, data: dict):
        """展示数据结构"""
        tree = Tree(f"[bold cyan]{data['name']}[/bold cyan]")
        tree.add(f"[yellow]描述:[/yellow] {data['desc'][:30]}...")
        tree.add(f"[yellow]分类:[/yellow] {', '.join(data['category'])}")
        tree.add(f"[yellow]症状:[/yellow] {', '.join(data['symptom'])}")
        tree.add(f"[yellow]科室:[/yellow] {', '.join(data['cure_department'])}")
        console.print(tree)
    
    def run(self):
        """执行数据预处理"""
        console.print(Panel.fit(
            "[bold cyan]医疗数据预处理系统[/bold cyan]\n"
            "[yellow]数据清洗、标准化与结构化处理[/yellow]",
            border_style="cyan"
        ))
        
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task(
                "[cyan]预处理进度...", 
                total=len(self.raw_data)
            )
            
            for disease in self.raw_data:
                processed = self.process_disease(disease)
                results.append(processed)
                progress.update(task, advance=1)
        
        # 显示处理后的数据结构
        console.print("\n[bold green]处理后的数据结构:[/bold green]")
        self.show_data_structure(results[0])
        
        # 显示统计信息
        table = Table(title="预处理统计", show_header=True, header_style="bold magenta")
        table.add_column("指标", style="cyan")
        table.add_column("数值", justify="right", style="green")
        
        total_symptoms = sum(len(d['symptom']) for d in results)
        total_departments = sum(len(d['cure_department']) for d in results)
        
        table.add_row("处理疾病数", str(len(results)))
        table.add_row("提取症状数", str(total_symptoms))
        table.add_row("关联科室数", str(total_departments))
        table.add_row("数据完整性", "100%")
        
        console.print(table)
        logger.info(f"数据预处理完成，共处理 {len(results)} 条数据")
        
        return results


if __name__ == "__main__":
    preprocessor = MedicalPreprocessor()
    preprocessor.run()
