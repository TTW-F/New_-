"""
测试 Neo4j 数据库是否有数据
"""

from neo4j_service import get_neo4j_service
from rich.console import Console
from rich.table import Table

console = Console()

def test_neo4j_data():
    """测试 Neo4j 数据"""
    console.print("[bold cyan]测试 Neo4j 数据库[/bold cyan]\n")
    
    service = get_neo4j_service()
    
    # 1. 测试连接
    console.print("[yellow]1. 测试连接...[/yellow]")
    try:
        with service.driver.session() as session:
            result = session.run("RETURN 1")
            result.single()
        console.print("[green]✓ 连接成功[/green]\n")
    except Exception as e:
        console.print(f"[red]✗ 连接失败: {e}[/red]\n")
        return
    
    # 2. 统计节点数量
    console.print("[yellow]2. 统计节点数量...[/yellow]")
    with service.driver.session() as session:
        # 疾病数量
        result = session.run("MATCH (d:Disease) RETURN count(d) as count")
        disease_count = result.single()["count"]
        
        # 症状数量
        result = session.run("MATCH (s:Symptom) RETURN count(s) as count")
        symptom_count = result.single()["count"]
        
        # 药品数量
        result = session.run("MATCH (d:Drug) RETURN count(d) as count")
        drug_count = result.single()["count"]
        
        # 检查数量
        result = session.run("MATCH (c:Check) RETURN count(c) as count")
        check_count = result.single()["count"]
    
    table = Table(title="节点统计")
    table.add_column("类型", style="cyan")
    table.add_column("数量", style="green")
    
    table.add_row("疾病 (Disease)", str(disease_count))
    table.add_row("症状 (Symptom)", str(symptom_count))
    table.add_row("药品 (Drug)", str(drug_count))
    table.add_row("检查 (Check)", str(check_count))
    
    console.print(table)
    console.print()
    
    # 3. 测试模糊搜索
    console.print("[yellow]3. 测试模糊搜索...[/yellow]")
    
    test_keywords = ["感冒", "头痛", "糖尿病", "高血压"]
    
    for keyword in test_keywords:
        results = service.fuzzy_search_entity(keyword, limit=3)
        console.print(f"搜索 '{keyword}': 找到 {len(results)} 个结果")
        for r in results:
            console.print(f"  - {r['name']} ({r['type']})")
    
    console.print()
    
    # 4. 查看示例数据
    console.print("[yellow]4. 查看示例疾病...[/yellow]")
    with service.driver.session() as session:
        result = session.run("MATCH (d:Disease) RETURN d.name as name LIMIT 5")
        diseases = [record["name"] for record in result]
        
        if diseases:
            console.print("前5个疾病:")
            for d in diseases:
                console.print(f"  - {d}")
        else:
            console.print("[red]数据库中没有疾病数据![/red]")
    
    console.print()
    console.print("[bold green]测试完成![/bold green]")

if __name__ == "__main__":
    test_neo4j_data()
