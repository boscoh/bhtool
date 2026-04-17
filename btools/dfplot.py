#!/usr/bin/env python3

"""Plot parquet files"""

from path import Path

import matplotlib as mpl
import pandas
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters

from btools.utils import open_path

register_matplotlib_converters()


def plot_df_columns_as_scatter(df):
    mpl.rcParams["xtick.labelsize"] = 6
    mpl.rcParams["ytick.labelsize"] = 6

    xlim = [df["time"].min(), df["time"].max()]
    cols = [c for c in df.columns.values if c != "time"]
    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    fig, axes = plt.subplots(len(cols), 1, sharex=True, figsize=(7, len(cols) * 1))
    for i, col in enumerate(cols):
        ax = axes[i]
        color = colors[i % len(colors)]
        ax.scatter(
            df["time"].values,
            df[col].values,
            label=col,
            s=3,
            c=color,
        )

        ax.set_title(col, color=color, fontdict={"fontsize": 10}, pad=0, loc="right")

        ax_color = (0.4, 0.4, 0.4)

        ax.tick_params(axis="x", colors=ax_color)
        ax.tick_params(axis="y", colors=ax_color)
        ax.yaxis.label.set_color(ax_color)
        ax.xaxis.label.set_color(ax_color)

        grid_box_border_color = (0.9, 0.9, 0.9)
        ax.spines["bottom"].set_color(grid_box_border_color)
        ax.spines["top"].set_color(grid_box_border_color)
        ax.spines["right"].set_color(grid_box_border_color)
        ax.spines["left"].set_color(grid_box_border_color)

    plt.subplots_adjust(hspace=0.4)
    plt.xlim(xlim)


def resample_df(df, interval="1s"):
    df = df.set_index("time")
    df.sort_index(inplace=True)
    df = df.resample(interval).mean()
    df.dropna(how="all", inplace=True)
    df.reset_index(inplace=True)
    return df


def _first_data_results_dir() -> Path:
    for p in Path().walkdirs():
        parts = p.parts()
        if len(parts) >= 2 and parts[-2] == "data" and parts[-1] == "results":
            return p
    raise FileNotFoundError("Could not find a directory matching **/data/results")


def dfplot_run():
    d = _first_data_results_dir()
    print(f"Found (**/data/results) directory: {d}")

    n = len(list(d.walkfiles("*.parquet")))
    print(f"Loading {n} parquet files...")

    df = pandas.read_parquet(d)

    if isinstance(df.index, pandas.DatetimeIndex):
        df = resample_df(df, "1s")

    out_f = Path("data_logger_results.png")
    print(f"Saving {out_f}")
    mpl.use("Agg")
    plot_df_columns_as_scatter(df)
    plt.savefig(out_f)

    open_path(out_f)
