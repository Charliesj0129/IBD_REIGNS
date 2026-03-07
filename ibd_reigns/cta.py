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
                CtaAction(label="下載衛教手冊", action_type="link", url="http://tasid.org.tw/upload/FileData/file/50/351.pdf"),
                CtaAction(label="IBD 官網", action_type="link", url="https://www.ibdpg.tw/"),
            ],
            footer="© 台灣發炎性腸道疾病學會",
        )
    if ending_type in {"bad_dropout", "bad_bankruptcy", "financial_toxicity"}:
        return CtaContent(
            title="你並不孤單",
            actions=[
                CtaAction(label="IBD 官網", action_type="link", url="https://www.ibdpg.tw/"),
                CtaAction(label="下載衛教手冊", action_type="link", url="http://tasid.org.tw/upload/FileData/file/50/351.pdf"),
            ],
            footer="© 台灣發炎性腸道疾病學會",
        )
    return CtaContent(
        title="恭喜達成深度緩解",
        actions=[
            CtaAction(label="IBD 官網", action_type="link", url="https://www.ibdpg.tw/"),
            CtaAction(label="下載衛教手冊", action_type="link", url="http://tasid.org.tw/upload/FileData/file/50/351.pdf"),
        ],
        footer="© 台灣發炎性腸道疾病學會",
    )
