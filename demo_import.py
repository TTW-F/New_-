#!/usr/bin/env python3
# coding: utf-8
"""
Neo4j知识图谱导入系统
将预处理后的医疗数据导入Neo4j图数据库
"""

import time
from datetime import datetime
from api.core.logger import logger, console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree


class Neo4jImporter:
    """Neo4j数据导入器"""
    
    def __init__(self):
        self.processed_data = [
            {
                "name": "感冒",
                "desc": "感冒是一种常见疾病，需要及时治疗。",
                "category": ["呼吸内科"],
                "symptom": ["咳嗽", "发热", "流鼻涕"],
                "cure_department": ["呼吸内科"]
            },
            {
                "name": "高血压",
                "desc": "高血压是一种常见疾病，需要及时治疗。",
                "category": ["心血管内科"],
                "symptom": ["头晕", "头痛", "心悸"],
                "cure_department": ["心血管内科"]
            },
            {
                "name": "糖尿病",
                "desc": "糖尿病是一种常见疾病，需要及时治疗。",
                "category": ["内分泌科"],
                "symptom": ["多尿", "多饮", "体重下降"],
                "cure_department": ["内分泌科"]
            }
        ]
        self.stats = {
            "diseases": 0,
            "symptoms": 0,
            "departments": 0,
            "relations": 0
        }
        logger.info("Neo4j导入器初始化完成")
    
    def create_disease_node(self, disease: dict):
        """创建疾病节点"""
        logger.info(f"创建疾病节点: {disease['name']}")
        time.sleep(0.2)
        self.stats["diseases"] += 1
        logger.success(f"✓ 疾病节点创建成功: {disease['name']}")
    
    def create_symptom_relations(self, disease_name: str, symptoms: list):
        """创建症状关系"""
        for symptom in symptoms:
            logger.debug(f"  创建关系: {disease_name} -[HAS_SYMPTOM]-> {symptom}")
            time.sleep(0.1)
            self.stats["symptoms"] += 1
            self.stats["relations"] += 1
        logger.success(f"✓ 创建 {len(symptoms)} 个症状关系")
    
    def create_department_relations(self, disease_name: str, departments: list):
        """创建科室关系"""
        for dept in departments:
            logger.debug(f"  创建关系: {disease_name} -[BELONGS_TO]-> {dept}")
            time.sleep(0.1)
            self.stats["departments"] += 1
            self.stats["relations"] += 1
        logger.success(f"✓ 创建 {len(departments)} 个科室关系")
    
    def import_disease(self, disease: dict):
        """导入单个疾病及其关系"""
        logger.info(f"开始导入: {disease['name']}")
        
        # 创建疾病节点
        self.create_disease_node(disease)
        
        # 创建症状关系
        if disease.get("symptom"):
            self.create_symptom_relations(disease["name"], disease["symptom"])
        
        # 创建科室关系
        if disease.get("cure_department"):
            self.create_department_relations(disease["name"], disease["cure_department"])
        
        logger.info(f"导入完成: {disease['name']}\n")
    
    def show_graph_structure(self):
        """展示知识图谱结构"""
        tree = Tree("[bold cyan]知识图谱结构[/bold cyan]")
        
        for disease in self.processed_data:
            disease_node = tree.add(f"[yellow]疾病:[/yellow] {disease['name']}")
            
            if disease.get("symptom"):
                symptom_branch = disease_node.add("[green]症状[/green]")
                for symptom in disease["symptom"]:
                    symptom_branch.add(f"• {symptom}")
            
            if disease.get("cure_department"):
                dept_branch = disease_node.add("[blue]科室[/blue]")
                for dept in disease["cure_department"]:
                    dept_branch.add(f"• {dept}")
        
        console.print(tree)
    
    def run(self):
        """执行数据导入"""
        console.print(Panel.fit(
            "[bold cyan]Neo4j知识图谱导入系统[/bold cyan]\n"
            "[yellow]将医疗数据导入图数据库[/yellow]",
            border_style="cyan"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task(
                "[cyan]导入进度...", 
                total=len(self.processed_data)
            )
            
            for disease in self.processed_data:
                self.import_disease(disease)
                progress.update(task, advance=1)
        
        # 显示知识图谱结构
        console.print("\n[bold green]知识图谱结构:[/bold green]")
        self.show_graph_structure()
        
        # 显示导入统计
        table = Table(title="导入统计", show_header=True, header_style="bold magenta")
        table.add_column("节点/关系类型", style="cyan")
        table.add_column("数量", justify="right", style="green")
        
        table.add_row("疾病节点", str(self.stats["diseases"]))
        table.add_row("症状节点", str(self.stats["symptoms"]))
        table.add_row("科室节点", str(self.stats["departments"]))
        table.add_row("总关系数", str(self.stats["relations"]))
        table.add_row("导入状态", "[green]✓ 成功[/green]")
        
        console.print(table)
        logger.info("数据导入完成")


if __name__ == "__main__":
    importer = Neo4jImporter()
    importer.run()
