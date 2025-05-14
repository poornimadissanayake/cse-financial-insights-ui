"use client"

import { Area, AreaChart, CartesianGrid, XAxis, YAxis } from "recharts"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import {
    ChartConfig,
    ChartContainer,
    ChartTooltip,
} from "@/components/ui/chart"
import { useState } from "react"
import { Company, QuarterlyReport, FinancialMetrics } from "@/lib/api"

interface CompanyComparisonChartProps {
    companies: Company[]
    companyData: {
        [key: string]: QuarterlyReport[]
    }
}

const METRIC_OPTIONS = [
    { value: "revenue", label: "Revenue" },
    { value: "cost_of_goods_sold", label: "Cost of Goods Sold (COGS)" },
    { value: "gross_profit", label: "Gross Profit" },
    { value: "distribution_costs", label: "Distribution Costs" },
    { value: "administrative_expenses", label: "Administrative Expenses" },
    { value: "operating_income", label: "Operating Income" },
    { value: "profit_before_tax", label: "Profit Before Tax" },
    { value: "net_income", label: "Net Income" },
    { value: "eps_basic", label: "EPS (Basic)" },
]

const METRIC_DESCRIPTIONS: { [key: string]: string } = {
    revenue: "Total income from sales before any costs are deducted.",
    cost_of_goods_sold: "Direct costs attributable to the production of goods sold.",
    gross_profit: "Gross Profit = Revenue - Cost of Goods Sold (COGS)",
    distribution_costs: "Expenses related to delivering products to customers.",
    administrative_expenses: "General overhead and administrative costs.",
    operating_income: "Operating Income = Gross Profit + Other Income - Distribution Costs - Administrative Expenses",
    profit_before_tax: "Profit before income tax is deducted.",
    net_income: "Net Income = Final profit after all expenses, finance items, and taxes.",
    eps_basic: "Earnings per share (basic).",
}

const COLORS = {
    REXP: "hsl(30, 100%, 50%)",    // Bright orange
    DIPD: "hsl(120, 100%, 20%)",   // Dark green
}

// Update calculateOperatingIncome with proper types
const calculateOperatingIncome = (metrics: FinancialMetrics | undefined) => {
    if (!metrics) return 0;

    const grossProfit = metrics.gross_profit || 0;
    const otherIncome = metrics.other_income || 0;
    const distributionCosts = Math.abs(metrics.distribution_costs || 0);
    const administrativeExpenses = Math.abs(metrics.administrative_expenses || 0);

    return grossProfit + otherIncome - distributionCosts - administrativeExpenses;
}

// List of currency metrics to show in millions
const currencyMetrics = [
    'revenue',
    'cost_of_goods_sold',
    'gross_profit',
    'other_income',
    'distribution_costs',
    'administrative_expenses',
    'operating_income',
    'finance_costs',
    'finance_income',
    'share_of_profit_equity_investee',
    'profit_before_tax',
    'tax_expense',
    'net_income',
];

const expenseMetrics = [
    'cost_of_goods_sold',
    'distribution_costs',
    'administrative_expenses',
];

const formatTooltipValue = (value: number | null | undefined, metric: string) => {
    if (value === null || value === undefined || isNaN(value)) return "N/A";
    if (currencyMetrics.includes(metric)) {
        return `${(value / 1_000_000).toFixed(2)}M`;
    }
    return value.toLocaleString();
};

const formatChartValue = (value: number | null | undefined, metric: string) => {
    if (value === null || value === undefined) return null;
    if (expenseMetrics.includes(metric)) {
        return Math.abs(value);
    }
    return value;
};

export function CompanyComparisonChart({ companies, companyData }: CompanyComparisonChartProps) {
    const [selectedMetric, setSelectedMetric] = useState(METRIC_OPTIONS[0].value)

    // Get all unique years from the data
    const allYears = new Set<string>()
    companies.forEach(company => {
        companyData[company.symbol].forEach(report => {
            allYears.add(report.year)
        })
    })
    const sortedYears = Array.from(allYears).sort()

    // State for year range
    const [startYear, setStartYear] = useState(sortedYears[0])
    const [endYear, setEndYear] = useState(sortedYears[sortedYears.length - 1])

    // Get all unique periods across all companies within the selected year range
    const allPeriods = new Set<string>()
    companies.forEach(company => {
        companyData[company.symbol].forEach(report => {
            if (report.year >= startYear && report.year <= endYear) {
                allPeriods.add(`${report.quarter} ${report.year}`)
            }
        })
    })

    // Transform data for the chart
    const chartData = Array.from(allPeriods).map(period => {
        interface DataPoint {
            period: string;
            [key: string]: string | number | null;
        }
        const dataPoint: DataPoint = { period }
        companies.forEach(company => {
            const report = companyData[company.symbol].find(
                r => `${r.quarter} ${r.year}` === period
            )
            
            let value: number | null;
            if (selectedMetric === 'operating_income') {
                value = report ? calculateOperatingIncome(report.financial_metrics) : null;
            } else {
                value = report?.financial_metrics[selectedMetric as keyof typeof report.financial_metrics] ?? null;
            }
            dataPoint[company.symbol] = formatChartValue(value, selectedMetric);
        })
        return dataPoint
    }).sort((a, b) => {
        // Sort by year first, then by quarter
        const [aQuarter, aYear] = a.period.split(" ")
        const [bQuarter, bYear] = b.period.split(" ")
        if (aYear !== bYear) {
            return aYear.localeCompare(bYear)
        }
        return aQuarter.localeCompare(bQuarter)
    })

    const chartConfig = companies.reduce((acc, company, index) => ({
        ...acc,
        [company.symbol]: {
            label: company.symbol,
            color: `hsl(var(--chart-${index + 1}))`,
        }
    }), {}) satisfies ChartConfig

    // Get the selected metric label
    const selectedMetricLabel = METRIC_OPTIONS.find(opt => opt.value === selectedMetric)?.label
    const selectedMetricDescription = METRIC_DESCRIPTIONS[selectedMetric] || ""

    // Determine if the metric is a cost/expense
    const isExpenseMetric = selectedMetric.includes('cost') ||
        selectedMetric.includes('expense') ||
        selectedMetric === 'cost_of_goods_sold'

    return (
        <Card>
            <CardHeader>
                <div className="flex justify-between items-start">
                    <div className="flex flex-col gap-2">
                        <CardTitle>
                            {companies.map(c => c.symbol).join(" vs ")} Financial Comparison
                        </CardTitle>
                        <CardDescription>
                            Comparing {selectedMetricLabel} between companies
                            {isExpenseMetric && " (Cost/Expense)"}
                        </CardDescription>
                        <div className="text-xs text-muted-foreground mt-1">
                            {selectedMetricDescription}
                        </div>
                        <div className="mt-2">
                            <Select value={selectedMetric} onValueChange={setSelectedMetric}>
                                <SelectTrigger className="w-[300px]">
                                    <SelectValue placeholder="Select metric" />
                                </SelectTrigger>
                                <SelectContent>
                                    {METRIC_OPTIONS.map(option => (
                                        <SelectItem key={option.value} value={option.value}>
                                            {option.label}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        {currencyMetrics.includes(selectedMetric) && (
                            <div className="text-xs text-muted-foreground mt-1">
                                All currency metrics are shown in LKR.
                            </div>
                        )}
                    </div>
                    <div className="flex gap-4 items-center">
                        <div className="flex items-center gap-2">
                            <span className="text-sm">From:</span>
                            <Select value={startYear} onValueChange={setStartYear}>
                                <SelectTrigger className="w-[100px]">
                                    <SelectValue placeholder="Start Year" />
                                </SelectTrigger>
                                <SelectContent>
                                    {sortedYears.map(year => (
                                        <SelectItem key={year} value={year}>
                                            {year}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="text-sm">To:</span>
                            <Select value={endYear} onValueChange={setEndYear}>
                                <SelectTrigger className="w-[100px]">
                                    <SelectValue placeholder="End Year" />
                                </SelectTrigger>
                                <SelectContent>
                                    {sortedYears.map(year => (
                                        <SelectItem key={year} value={year}>
                                            {year}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </div>
                </div>
            </CardHeader>
            <CardContent>
                <ChartContainer config={chartConfig}>
                    <AreaChart
                        accessibilityLayer
                        data={chartData}
                        height={400}
                        margin={{
                            top: 10,
                            right: 30,
                            left: 30,
                            bottom: 0,
                        }}
                    >
                        <defs>
                            <linearGradient id="fillREXP" x1="0" y1="0" x2="0" y2="1">
                                <stop
                                    offset="5%"
                                    stopColor="var(--chart-1)"
                                    stopOpacity={0.8}
                                />
                                <stop
                                    offset="95%"
                                    stopColor="var(--chart-1)"
                                    stopOpacity={0.1}
                                />
                            </linearGradient>
                            <linearGradient id="fillDIPD" x1="0" y1="0" x2="0" y2="1">
                                <stop
                                    offset="5%"
                                    stopColor="var(--chart-2)"
                                    stopOpacity={0.8}
                                />
                                <stop
                                    offset="95%"
                                    stopColor="var(--chart-2)"
                                    stopOpacity={0.1}
                                />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                        <XAxis
                            dataKey="period"
                            tickLine={false}
                            axisLine={false}
                            tickMargin={8}
                            minTickGap={0}
                        />
                        <YAxis
                            tickLine={false}
                            axisLine={false}
                            tickMargin={8}
                            width={80}
                            domain={[
                                dataMin => Math.min(0, dataMin * 1.1),
                                dataMax => dataMax * 1.1
                            ]}
                            tickFormatter={(value) => {
                                // List of currency metrics to show in millions
                                const currencyMetrics = [
                                    'revenue',
                                    'cost_of_goods_sold',
                                    'gross_profit',
                                    'other_income',
                                    'distribution_costs',
                                    'administrative_expenses',
                                    'operating_income',
                                    'finance_costs',
                                    'finance_income',
                                    'share_of_profit_equity_investee',
                                    'profit_before_tax',
                                    'tax_expense',
                                    'net_income',
                                ];
                                if (currencyMetrics.includes(selectedMetric)) {
                                    return `${(value / 1_000_000).toFixed(1)}M`;
                                }
                                return value.toLocaleString();
                            }}
                        />
                        <ChartTooltip
                            cursor={false}
                            content={({ active, payload, label }) => {
                                if (active && payload && payload.length) {
                                    return (
                                        <div className="bg-background border rounded-lg p-4 shadow-lg">
                                            <p className="font-bold mb-2">{label}</p>
                                            {payload.map((entry, idx) => (
                                                <p key={entry.name}>
                                                    <span className="font-semibold">{entry.name}:</span> {selectedMetricLabel}: {
                                                        formatTooltipValue(entry.value, selectedMetric)
                                                    }
                                                </p>
                                            ))}
                                        </div>
                                    );
                                }
                                return null;
                            }}
                        />
                        {companies.map((company) => (
                            <Area
                                key={company.symbol}
                                type="natural"
                                dataKey={company.symbol}
                                fill={company.symbol === 'REXP' ? 'rgba(255,165,0,0.2)' : `url(#fill${company.symbol})`}
                                fillOpacity={0.4}
                                stroke={COLORS[company.symbol as keyof typeof COLORS]}
                            />
                        ))}
                    </AreaChart>
                </ChartContainer>
            </CardContent>
            <CardFooter>
                <div className="flex w-full items-start justify-between gap-2 text-sm">
                    <div className="grid gap-2">
                        <div className="flex items-center gap-2 font-medium leading-none">
                            {selectedMetricLabel} Comparison
                            {isExpenseMetric && " (Cost/Expense)"}
                        </div>
                        <div className="flex items-center gap-2 leading-none text-muted-foreground">
                            {companies.map(c => c.symbol).join(" vs ")}
                        </div>
                        {expenseMetrics.includes(selectedMetric) && (
                            <div className="text-xs text-muted-foreground mt-1">
                                Expenses are shown as positive values for easier comparison.
                            </div>
                        )}
                    </div>
                    <div className="flex items-center gap-4">
                        {companies.map((company) => (
                            <div key={company.symbol} className="flex items-center gap-2">
                                <div
                                    className="w-3 h-3 rounded-sm"
                                    style={{ backgroundColor: COLORS[company.symbol as keyof typeof COLORS] }}
                                />
                                <span>{company.symbol}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </CardFooter>
        </Card>
    )
} 