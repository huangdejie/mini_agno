from fastmcp import FastMCP

mcp = FastMCP()


@mcp.tool
def query_temperature(bake_house: str) -> str:
    """根据烤房查询烤房的温度"""
    return "38.2"


@mcp.tool
def query_humidity(bake_house: str) -> str:
    """根据烤房查询烤房的湿度"""
    return "80.1"


if __name__ == "__main__":
    mcp.run()
