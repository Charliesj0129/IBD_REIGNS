from dataclasses import dataclass
from typing import List


@dataclass
class CtaAction:
    label: str
    action_type: str
    url: str | None = None


@dataclass
class CtaContent:
    title: str
    actions: List[CtaAction]
    footer: str


def build_cta(ending_type: str) -> CtaContent:
    if ending_type in {"bad_sepsis", "bad_perforation", "bad_megacolon", "bad_end"}:
        return CtaContent(
            title="別讓這成為現實",
            actions=[
                CtaAction(label="下載衛教指引", action_type="link", url="https://www.tsibd.org.tw/editor_images/File/TSIBD-201810.pdf"),
                CtaAction(label="尋找專科醫師", action_type="link", url="https://www.tsibd.org.tw/ibd_dr"),
            ],
            footer="© 台灣炎症性腸道疾病病友協會",
        )
    if ending_type in {"bad_dropout", "bad_bankruptcy", "financial_toxicity"}:
        return CtaContent(
            title="你並不孤單",
            actions=[
                CtaAction(label="加入病友社群", action_type="link", url="https://www.facebook.com/TaiwanIBD/"),
                CtaAction(label="社福資源總覽", action_type="link", url="https://www.tsibd.org.tw/patients/"),
            ],
            footer="© 台灣炎症性腸道疾病病友協會",
        )
    return CtaContent(
        title="恭喜達成深度緩解",
        actions=[
            CtaAction(label="加入病友社群", action_type="link", url="https://www.facebook.com/TaiwanIBD/"),
            CtaAction(label="社福資源總覽", action_type="link", url="https://www.tsibd.org.tw/patients/"),
        ],
        footer="© 台灣炎症性腸道疾病病友協會",
    )
