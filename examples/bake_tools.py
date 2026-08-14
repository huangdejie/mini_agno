from mini_agno.tools.decorator import my_tool


@my_tool
def query_bake_info(district: str) -> dict:
    """根据地区查询烘烤信息"""
    if district == "beijing":
        return {"bake_info": "beijing bake info"}
    elif district == "shanghai":
        return {"bake_info": "shanghai bake info"}
    else:
        return {"bake_info": "other district bake info"}
