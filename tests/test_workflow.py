from mini_agno import workflow
from mini_agno.agent import Agent
from mini_agno.models.message import ModelResponse
from mini_agno.models.mock import MockModel
from mini_agno.models.openai_model import OpenAIModel
from mini_agno.workflow.condition import Condition
from mini_agno.workflow.step import Step
from mini_agno.workflow.workflow import Workflow

NEWS_TEXT = """
            # 上半年新车销量中新能源占比近50%，传统燃油车市场进一步萎缩
            7月9日，中国汽车工业协会公布的最新数据显示，今年1至6月份，我国新能源汽车市场产销量、出口量均呈现稳定增长态势。新能源汽车产销量分别完成743.8万辆和744.6万辆，同比分别增长6.7%和7.3%，新能源汽车新车销量达到汽车新车总销量的49.6%。
            在出口方面，1至6月份，汽车出口509.6万辆，同比增长65.3%。其中新能源汽车出口235.5万辆，同比增长1.2倍。
            中国汽车工业协会副秘书长陈士华表示，今年以来，新能源汽车出口成为拉动汽车出口增长的核心动力。出口的快速增长，是我国汽车产业转型升级、国际竞争力提升的集中体现。
            就今年上半年汽车行业整体情况来看，中国汽车工业协会指出，我国汽车行业运行总体平稳，产销累计降幅逐月收窄。市场流向主要呈现出三个分化：一是内需承压明显，销量两位数下降；出口超预期增长，形成稳定支撑。二是乘用车市场表现欠佳，出现小幅下滑；商用车市场延续向好态势，销量保持增长。三是产业新旧动能持续转换，传统燃油车市场进一步萎缩，新能源汽车稳定增长。
            单看6月，新能源汽车产销单月分别完成159.8万辆和164.3万辆，同比增长均超两成，新能源汽车新车销量占汽车新车总销量的比例进一步提升，达到58.5%。这意味着，当月每十台完成交易的新车里，近六台为纯电、插混等新能源车型，传统燃油车剩余市场空间被持续压缩。
            新能源汽车内销方面，6月单月销量为112万辆，同比下降0.4%。其中，新能源乘用车国内销量100.7万辆，同比下降4.5%；新能源商用车国内销量11.3万辆，同比增长61%。
            1-6月，新能源汽车国内销量509万辆，同比下降13.4%。其中，新能源乘用车国内销量459.4万辆，同比下降16.8%；新能源商用车国内销量49.6万辆，同比增长40.2%。
            新能源汽车国内销量占比在逐月提升。6月，新能源汽车国内销量比例为63.1%；新能源乘用车国内销量占乘用车国内销量比例为67.2%；新能源商用车国内销量占商用车国内销量比例为40.9%。
            1-6月，新能源汽车国内销量比例为51.3%；新能源乘用车国内销量占乘用车国内销量比例为55.4%；新能源商用车国内销量占商用车国内销量比例为30.4%。
            而在出口方面，新能源汽车的表现也颇为亮眼。6月，新能源汽车出口52.3万辆，同比增长1.6倍。其中，新能源乘用车出口51万辆，同比增长1.6倍；新能源商用车出口1.3万辆，同比增长60.9%。
            反观燃油车的处境，基本处于下滑态势。6月，汽车国内销量完成177.3万辆，同比下降23.3%。其中，传统燃料汽车国内销量65.4万辆，同比下降45%。1-6月，汽车国内销量992.1万辆，同比下降21.1%，传统燃料汽车国内销量483.1万辆，同比下降27.8%。
            燃油乘用车是拖累国内乘用车销量走弱的核心因素。国内消费意愿不足叠加新能源产品供给丰富等因素，持续挤压燃油车生存空间，合资燃油品牌份额加速缩水，自主品牌燃油车型也同步收缩产能，行业资源持续向新能源研发、产线倾斜。
            国内市场油电格局失衡的同时，海外市场成为新能源全新增长极，有效对冲国内燃油车下滑带来的销量缺口。
            中国汽车工业协会发布的数据显示，6月国内汽车整车出口量历史性突破百万台关口，当月出口103.7万辆，同比大幅上涨75.1%，上半年累计出口规模达到509.6万辆，海外渠道正式成为行业稳定增长的核心支撑。
            海外市场新能源车型热销，进一步放大燃油车的市场劣势。海外消费者对电动车型接受度持续走高，自主品牌依托完善的三电、智能座舱技术形成差异化优势，燃油车型仅在部分欠发达市场保留少量需求，全球范围内燃油车收缩趋势与国内市场形成共振。
            而围绕重点汽车企业销量情况来看，1-6月，新能源汽车销量排名前十五位的集团销量合计为720.9万辆，同比增长7.1%，占新能源汽车销售总量的96.8%，低于去年同期0.2个百分点。前三名分别为比亚迪、吉利、上汽，市场集中度则为47.6%。
            整车出口前十企业中，1-6月，奇瑞出口93.9万辆，同比增长71.3%，占出口总量的18.4%。与去年同期相比，吉利出口增速最为显著，出口达58.5万辆，同比增长1.5倍。
            针对下半年行业走势，中汽协发布报告指出，“两新”政策将继续有序实施，汽车后市场消费有望迎来新的增量机遇，企业新品供给持续丰富，市场价格相对稳定，行业整体经济运行将进一步好转。同时也要看到，外部形势复杂多变、不确定性持续增加，内需不足问题依然突出，行业运行仍面临较大压力。需要稳定政策预期，强化引导监管，密切关注国际形势变化，有效应对风险挑战，稳步开拓国际市场。
        """

def search_news(input: str):
        return NEWS_TEXT




def test_seq_workflow():
    step1 = Step(name="search_news", func=search_news)
    response_list = [ModelResponse(content="上半年新车销量中新能源占比近50%，传统燃油车市场进一步萎缩")]
    step2 = Step(name="总结新闻信息", agent=Agent(model=MockModel(id="1", response_list=response_list),tools=[]))
    workflow = Workflow(steps=[step1, step2])
    resp = workflow.run("帮我查看最新的新闻")
    print(resp)
    assert "燃油" in resp

def search_connect_info(input: str):
    if "新闻" in input:
        return "mongodb://localhost:27017/"
    else:
        return "jdbc://localhost:3306/test_abcd"

def judge_mysql_connect_info(input: str):
    if "mongodb:" in input:
        return False
    else:
        return True

def test_condition_workflow():
    step1 = Step(name="search_connect_info", func=search_connect_info)

    then_step_01 = Step(name="从DB中获取相关数据", func=lambda x: "姓名:张三,性别:男,年龄:18")
    then_step_02 = Step(name="获取姓名", func=lambda x: "张三")
    else_step_01 = Step(name="从MONGODB中获取相关数据", func=lambda x: "上半年新车销量中新能源占比近50%，传统燃油车市场进一步萎缩")
    else_step_02 = Step(name="提取重要信息", func=lambda x: "新能源占比逐年增高")

    then_steps = [then_step_01, then_step_02]   
    else_steps = [else_step_01, else_step_02]

    condition = Condition(name="从DB中获取相关数据", condition=judge_mysql_connect_info, then_steps=then_steps, else_steps=else_steps)

    workflow = Workflow(steps=[step1, condition])
    resp = workflow.run("帮我查询年龄最大的人员姓名")
    print(resp)
    assert resp == '张三'

    resp = workflow.run("帮我查询最新的新闻")
    print(resp)
    assert resp == '新能源占比逐年增高'
