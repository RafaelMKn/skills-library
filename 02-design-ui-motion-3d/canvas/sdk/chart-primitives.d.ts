/**
 * Chart primitives for `cursor/canvas` — multi-series, stacked, and pie charts
 * rendered as pure inline SVG with zero external dependencies.
 *
 * Distilled from the portal-website Highcharts analytics charting layer.
 */
import type { CSSProperties, JSX } from "react";
/**
 * Semantic tone for a chart series or slice. Mirrors the tone vocabulary
 * used by `Stat`, `Pill`, `Table`, and other SDK primitives so colors
 * match across a canvas — e.g. a `Stat tone="success"` and a
 * `ChartSeries tone="success"` render in the same green.
 *
 * Omit `tone` to let the chart auto-assign a distinct color from the
 * chart palette; supply `tone` only when the value carries semantic
 * meaning that should match other tonal elements on the page.
 */
export type ChartTone = "success" | "danger" | "warning" | "info" | "neutral";
/** A single labeled value, used by `PieChart`. */
export type ChartDataPoint = {
    label: string;
    /** Non-negative numeric value. */
    value: number;
};
/**
 * A named data series for `BarChart` and `LineChart`.
 * The `data` array aligns by index with the parent component's `categories`.
 * If `tone` is omitted, a color is auto-assigned from the chart palette.
 */
export type ChartSeries = {
    name: string;
    data: number[];
    tone?: ChartTone;
};
export type BarChartProps = {
    /** Category labels along the independent axis. */
    categories: string[];
    /** One or more data series. Values align by index with `categories`. */
    series: ChartSeries[];
    height?: number;
    /** Stack series on top of each other instead of grouping side-by-side. */
    stacked?: boolean;
    /** Render horizontal bars instead of vertical columns. */
    horizontal?: boolean;
    /** Show as 100% stacked (implies `stacked`). */
    normalized?: boolean;
    /** Suffix for y-axis tick labels (e.g. "%"). */
    valueSuffix?: string;
    style?: CSSProperties;
};
export type LineChartProps = {
    categories: string[];
    series: ChartSeries[];
    height?: number;
    /** Fill the area under each line with a soft tint. */
    fill?: boolean;
    valueSuffix?: string;
    style?: CSSProperties;
};
export type PieChartProps = {
    data: Array<ChartDataPoint & {
        tone?: ChartTone;
    }>;
    size?: number;
    donut?: boolean;
    style?: CSSProperties;
};
/**
 * Multi-series bar/column chart with optional stacking and normalization.
 * Distilled from the portal-website Highcharts analytics charts.
 *
 * Pass `categories` for x-axis labels and one or more `series` whose `data`
 * arrays align by index. With a single series you get simple bars; with
 * multiple series the default is grouped (side-by-side) — set `stacked` for
 * stacked columns or `normalized` for 100%-stacked share-mode.
 *
 * Colors are auto-assigned from the chart palette. With a **single series**,
 * each bar gets a different color by category (so a chart of 5 categories
 * shows 5 colors out of the box). With **multiple series**, each series gets
 * its own color. A legend appears when there are 2+ series.
 *
 * For semantic coloring, pass `tone` on a series — it maps to the same
 * palette entries used by `Stat`, `Pill`, and `Table` so your chart matches
 * tonal elements elsewhere on the page.
 *
 * @example
 * ```tsx
 * // Simple single-series
 * <BarChart
 *   categories={["Mon", "Tue", "Wed"]}
 *   series={[{ name: "Requests", data: [120, 90, 150] }]}
 * />
 *
 * // Stacked multi-series (like portal AI commit chart)
 * <BarChart
 *   categories={["Mon", "Tue", "Wed"]}
 *   series={[
 *     { name: "IDE", data: [120, 90, 150] },
 *     { name: "CLI", data: [30, 40, 25] },
 *     { name: "Cloud", data: [50, 60, 70] },
 *   ]}
 *   stacked
 * />
 *
 * // Semantic tones — "accepted" renders in the same green as
 * // <Stat tone="success"> elsewhere on the page.
 * <BarChart
 *   categories={["Mon", "Tue", "Wed"]}
 *   series={[
 *     { name: "Accepted", data: [70, 80, 60], tone: "success" },
 *     { name: "Rejected", data: [30, 20, 40], tone: "danger" },
 *   ]}
 *   stacked
 * />
 * ```
 */
export declare function BarChart({ categories, series, height, stacked, horizontal, normalized, valueSuffix, style }: BarChartProps): JSX.Element;
/**
 * Multi-series line chart with optional area fill. Distilled from the
 * portal-website Highcharts analytics charts.
 *
 * Each series draws a polyline with dot markers at each data point.
 * Set `fill` to shade the area under every line. Hover over any category
 * column to see a tooltip with all series values at that point.
 *
 * This is **not** a time-series component — it does not parse dates.
 * Pass pre-formatted date strings as `categories` if plotting over time.
 *
 * Colors are auto-assigned from the chart palette. For semantic coloring,
 * pass `tone` on a series — it maps to the same palette entries used by
 * `Stat`, `Pill`, and `Table`.
 *
 * @example
 * ```tsx
 * // Single line
 * <LineChart
 *   categories={["Jan", "Feb", "Mar", "Apr"]}
 *   series={[{ name: "Revenue", data: [100, 140, 120, 180] }]}
 * />
 *
 * // Multi-series with area fill
 * <LineChart
 *   categories={["Jan", "Feb", "Mar", "Apr"]}
 *   series={[
 *     { name: "Accepted", data: [50, 70, 60, 90] },
 *     { name: "Suggested", data: [120, 140, 130, 160] },
 *   ]}
 *   fill
 * />
 *
 * // Semantic tones — "errors" renders in the same red as a
 * // <Pill tone="danger"> elsewhere on the page.
 * <LineChart
 *   categories={["00:00", "06:00", "12:00", "18:00"]}
 *   series={[
 *     { name: "p95 latency", data: [80, 95, 110, 90], tone: "info" },
 *     { name: "errors", data: [2, 4, 9, 3], tone: "danger" },
 *   ]}
 * />
 * ```
 */
export declare function LineChart({ categories, series, height, fill, valueSuffix, style }: LineChartProps): JSX.Element;
/**
 * Pie (or donut) chart with hover highlighting. Distilled from the
 * portal-website Highcharts analytics charts.
 *
 * Unlike `BarChart` and `LineChart`, `PieChart` takes a flat `data` array of
 * `{ label, value }` points — each slice is its own category. Colors are
 * auto-assigned from the chart palette; pass `tone` on a point to give a
 * slice a semantic color that matches other tonal elements on the page.
 *
 * Hovering a slice expands it outward and dims the others; hovering a legend
 * item does the same. A tooltip with value and percentage appears below the
 * chart. Set `donut` for a hollow center.
 *
 * **Do not** use for bar-style comparisons — use `BarChart` instead.
 *
 * @example
 * ```tsx
 * // Basic pie
 * <PieChart
 *   data={[
 *     { label: "IDE", value: 120 },
 *     { label: "CLI", value: 30 },
 *     { label: "Cloud", value: 50 },
 *   ]}
 * />
 *
 * // Donut with semantic tones
 * <PieChart
 *   data={[
 *     { label: "Passing", value: 70, tone: "success" },
 *     { label: "Failing", value: 30, tone: "danger" },
 *   ]}
 *   donut
 * />
 * ```
 */
export declare function PieChart({ data, size, donut, style }: PieChartProps): JSX.Element;
//# sourceMappingURL=chart-primitives.d.ts.map