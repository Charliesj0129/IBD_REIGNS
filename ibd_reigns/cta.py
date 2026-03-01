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
                CtaAction(label="🏥 IBD 病友會", action_type="link", url="https://www.ibdpg.tw/tw"),
                CtaAction(label="📖 IBD 衛教手冊", action_type="link", url="http://www.tsibd.org.tw/editor_images/File/TSIBD-201810.pdf"),
            ],
            footer="© 台灣炎症性腸道疾病病友協會",
        )
    if ending_type in {"bad_dropout", "bad_bankruptcy", "financial_toxicity"}:
        return CtaContent(
            title="你並不孤單",
            actions=[
                CtaAction(label="🏥 IBD 病友會", action_type="link", url="https://www.ibdpg.tw/tw"),
                CtaAction(label="📖 IBD 衛教手冊", action_type="link", url="http://www.tsibd.org.tw/editor_images/File/TSIBD-201810.pdf"),
            ],
            footer="© 台灣炎症性腸道疾病病友協會",
        )
    return CtaContent(
        title="恭喜達成深度緩解",
        actions=[
            CtaAction(label="🏥 IBD 病友會", action_type="link", url="https://www.ibdpg.tw/tw"),
            CtaAction(label="📖 IBD 衛教手冊", action_type="link", url="https://www.tsibd.org.tw/editor_images/File/TSIBD-201810.pdf"),
        ],
        footer="© 台灣炎症性腸道疾病病友協會",
    )
