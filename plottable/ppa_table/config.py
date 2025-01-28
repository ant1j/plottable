from pathlib import Path

from plottable.column_def import ColumnDefinition, RichTextColumnDefinition
from plottable.formatters import decimal_to_percent
from plottable.plots import bar
from plottable.ppa_table.formats import (
    fontcolour_from_value,
    group_label_format,
    kdollar,
    pct,
    percentage_points,
    text_cmap_3cols,
)

###### LOAD #######

# EXCEL_PATH = Path(r"G:\Drive partagés\CL_Chanel APAC\2024 PPA\4.Excels")
EXCEL_PATH = Path(r"G:\Drive partagés\CL_Chanel APAC\2024\2024 PPA\4.Excels")
assert EXCEL_PATH.exists()

APAC_file = EXCEL_PATH / "2024 - Chanel PPA Asia - Global APAC - V0.5.xlsx"
CHN_file = EXCEL_PATH / "Par marché" / "2024 - Chanel PPA Asia - China - V0.2.xlsx"
AUS_file = EXCEL_PATH / "Par marché" / "2024 - Chanel PPA Asia - Australie - V0.4.xlsx"

tabs = {
    "recruitment": "SAS 12.1 RECRUT REACH SSCAT",
    "conversion": "SAS 12.1b Focus converties",
    "generation": "SAS 12.2 RECRUT REACH SSCAT GYZ",
    "labels_mappings": "Params",
}

CACHE_DATA_PATH = (
    Path(r"C:\Users\a.jouanjean\htdocs\plottable\scratchpad")
    / "data"
    / "data - AUS.pickle"
)


LOAD_PARAMS = {"region": APAC_file, "market": AUS_file, "tabs": tabs}

##### QUERY ####

QUERY_TEMPLATES = {
    "subcat": "macro_categorie == '{macro_categorie}' and nom_micro_categorie == '{nom_micro_categorie}'",
    "category": "nom_micro_categorie == 'categorie_cv' and micro_categorie == '{macro_categorie}'",
}


first_purch_to_cols = [
    "ca_prem_ach_only_ty",
    "ca_prem_ach_xsell_ty",
    "ca_prem_ach_ty",
]
first_purch_to_cols_evol = [
    "evol_ca_prem_ach_only",
    "evol_ca_prem_ach_xsell",
    "evol_ca_prem_ach",
]


cols_for_table = [
    "nom_micro_categorie",
    "macro_categorie",
    "micro_categorie",
    "entry_label",
    "first_purch_to",
    "evol_first_purch_to",
    "share_of_entry_ty",
    "evol_share_of_entry",
    "recr_index_ty",
    "evol_recr_index",
    "repeat_rate_ty",
    "evol_repeat_rate",
    "repeat_to_ty",
    "evol_repeat_to",
    "nb_cli_ty",
]

############### RichTable #####################

group_label_style = [
    dict(fontsize=14, weight="demibold"),
    dict(style="italic"),
]


group_props = {
    "Entry T.O.\n(2023)": group_label_style,
    "Share of entry\n(2023)": group_label_style,
    "Recruitment Index\n(2023)": group_label_style,
    "Repeat Rate\n(24 months)": group_label_style,
    "Repeat T.O.\n(24 months)": group_label_style,
}

column_definitions = [
    ColumnDefinition(
        name="micro_categorie",
        title=" ",
        width=1.25,
        textprops=dict(weight="demi", color="grey", size=11),
    ),
    RichTextColumnDefinition(
        name="entry_label",
        title=" ",
        width=0.65,
        textprops=dict(ha="right"),
        richtext_props=lambda x: {},
        boxprops=dict(ha="right", va="center"),
        formatter=(lambda X: f"CJ {X}" if X.endswith("ly:") else X),
    ),
    RichTextColumnDefinition(
        name="first_purch_to",
        title=" ",
        group=group_label_format("Entry T.O.", "(2023)"),
        width=0.3,
        formatter=kdollar,
        textprops=dict(ha="right"),
        richtext_props=lambda x: {},
        boxprops=dict(ha="right", va="center"),
    ),
    RichTextColumnDefinition(
        name="evol_first_purch_to",
        title="vs LY.",
        group=group_label_format("Entry T.O.", "(2023)"),
        width=0.3,
        formatter=pct,
        textprops={"ha": "right"},
        richtext_props=fontcolour_from_value,
    ),
    ColumnDefinition(
        "share_of_entry_ty",
        group=group_label_format("Share of entry", "(2023)"),
        title=" ",
        width=1.5,
        plot_fn=bar,
        plot_kw={
            "annotate": True,
            "height": 0.95,
            "lw": 0.0,
            "xlim": (-0.01, 0.5),  # TODO dynamic max
            "formatter": decimal_to_percent,
            "color": "#d2b496",
        },
    ),
    ColumnDefinition(
        name="evol_share_of_entry",
        title="vs LY.",
        group=group_label_format("Share of entry", "(2023)"),
        width=0.3,
        formatter=percentage_points,
        # textprops={"family": "sans-serif"},
        textprops={"family": "Segoe UI Symbol"},
        text_cmap=text_cmap_3cols,
    ),
    ColumnDefinition(
        name="recr_index_ty",
        title=" ",
        group=group_label_format("Recruitment Index", "(2023)"),
        width=0.5,
        # formatter=pct,
    ),
    ColumnDefinition(
        name="evol_recr_index",
        title="vs LY.",
        group=group_label_format("Recruitment Index", "(2023)"),
        width=0.3,
        formatter=pct,
        text_cmap=text_cmap_3cols,
    ),
    ColumnDefinition(
        "repeat_rate_ty",
        title=" ",
        group=group_label_format("Repeat Rate", "(24 months)"),
        width=1.5,
        plot_fn=bar,
        plot_kw={
            "annotate": True,
            "height": 0.95,
            "lw": 0.0,
            "xlim": (-0.01, 0.75),  # TODO dynamic max
            "formatter": decimal_to_percent,
            "color": "#d2b496",
        },
    ),
    ColumnDefinition(
        name="evol_repeat_rate",
        title="vs LY.",
        group=group_label_format("Repeat Rate", "(24 months)"),
        formatter=percentage_points,
        textprops={"family": "sans-serif"},
        text_cmap=text_cmap_3cols,
        width=0.3,
    ),
    ColumnDefinition(
        name="repeat_to_ty",
        title=" ",
        group=group_label_format("Repeat T.O.", "(24 months)"),
        formatter=kdollar,
        width=0.5,
    ),
    ColumnDefinition(
        name="evol_repeat_to",
        title="vs LY.",
        group=group_label_format("Repeat T.O.", "(24 months)"),
        formatter=pct,
        text_cmap=text_cmap_3cols,
        width=0.3,
    ),
]
