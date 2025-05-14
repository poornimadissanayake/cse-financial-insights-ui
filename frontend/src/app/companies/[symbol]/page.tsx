import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getCompanyFinancials } from "@/lib/api";
import { notFound } from "next/navigation";
import {
    Table,
    TableHeader,
    TableBody,
    TableRow,
    TableHead,
    TableCell,
} from "@/components/ui/table";
import Link from "next/link";

const COMPANY_NAMES: { [key: string]: string } = {
    "DIPD": "Dipped Products PLC",
    "REXP": "Richard Pieris Exports PLC",
};

interface PageProps {
    params: Promise<{
        symbol: string;
    }>;
}

export default async function CompanyPage({ params }: PageProps) {
    const { symbol } = await params;
    const reports = await getCompanyFinancials(symbol);

    if (!reports.length) {
        notFound();
    }

    const latestReport = reports[reports.length - 1];
    const metrics = latestReport.financial_metrics;
    const companyName = COMPANY_NAMES[symbol] || symbol;

    return (
        <main className="container mx-auto py-10">
            <Link href="/" className="inline-block mb-4 text-muted-foreground hover:text-foreground transition-colors text-sm font-medium">
                &larr; Back to Dashboard
            </Link>
            <h1 className="text-3xl font-bold mb-2">{companyName}</h1>
            <h2 className="text-2xl font-semibold mb-4">Latest Quarter ({latestReport.quarter} {latestReport.year})</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                <Card>
                    <CardHeader>
                        <CardTitle>
                            Revenue
                            <div className="text-xs text-muted-foreground font-normal">LKR '000</div>
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-2xl font-bold">
                            {metrics.revenue != null ? (metrics.revenue / 1000).toLocaleString() : "N/A"}
                        </p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader>
                        <CardTitle>
                            Net Income
                            <div className="text-xs text-muted-foreground font-normal">LKR '000</div>
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-2xl font-bold">
                            {metrics.net_income != null ? (metrics.net_income / 1000).toLocaleString() : "N/A"}
                        </p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader>
                        <CardTitle>EPS (Basic)</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-2xl font-bold">
                            {metrics.eps_basic != null ? metrics.eps_basic.toFixed(2) : "N/A"}
                        </p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader>
                        <CardTitle>Dividend per Share</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-2xl font-bold">
                            {metrics.dividend_per_share != null ? metrics.dividend_per_share.toFixed(2) : "N/A"}
                        </p>
                    </CardContent>
                </Card>
            </div>

            <h2 className="text-2xl font-semibold mb-4">Past Quarter Financials</h2>
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead style={{ position: 'sticky', left: 0, background: 'white', zIndex: 2, minWidth: 80 }}>Quarter</TableHead>
                        <TableHead style={{ position: 'sticky', left: 80, background: 'white', zIndex: 2, minWidth: 80 }}>Year</TableHead>
                        <TableHead className="text-right">Revenue</TableHead>
                        <TableHead className="text-right">Cost of Goods Sold</TableHead>
                        <TableHead className="text-right">Gross Profit</TableHead>
                        <TableHead className="text-right">Other Income</TableHead>
                        <TableHead className="text-right">Distribution Costs</TableHead>
                        <TableHead className="text-right">Administrative Expenses</TableHead>
                        <TableHead className="text-right">Operating Income</TableHead>
                        <TableHead className="text-right">Finance Costs</TableHead>
                        <TableHead className="text-right">Finance Income</TableHead>
                        <TableHead className="text-right">Share of Profit Equity Investee</TableHead>
                        <TableHead className="text-right">Profit Before Tax</TableHead>
                        <TableHead className="text-right">Tax Expense</TableHead>
                        <TableHead className="text-right">Net Income</TableHead>
                        <TableHead className="text-right">EPS (Basic)</TableHead>
                        <TableHead className="text-right">EPS (Diluted)</TableHead>
                        <TableHead className="text-right">Dividend per Share</TableHead>
                    </TableRow>
                    <TableRow>
                        <TableHead style={{ position: 'sticky', left: 0, background: 'white', zIndex: 2, minWidth: 80 }}></TableHead>
                        <TableHead style={{ position: 'sticky', left: 80, background: 'white', zIndex: 2, minWidth: 80 }}></TableHead>
                        <TableHead className="font-normal text-xs text-muted-foreground text-right">(LKR '000)</TableHead>
                        <TableHead className="font-normal text-xs text-muted-foreground text-right">(LKR '000)</TableHead>
                        <TableHead className="font-normal text-xs text-muted-foreground text-right">(LKR '000)</TableHead>
                        <TableHead className="font-normal text-xs text-muted-foreground text-right">(LKR '000)</TableHead>
                        <TableHead className="font-normal text-xs text-muted-foreground text-right">(LKR '000)</TableHead>
                        <TableHead className="font-normal text-xs text-muted-foreground text-right">(LKR '000)</TableHead>
                        <TableHead className="font-normal text-xs text-muted-foreground text-right">(LKR '000)</TableHead>
                        <TableHead className="font-normal text-xs text-muted-foreground text-right">(LKR '000)</TableHead>
                        <TableHead className="font-normal text-xs text-muted-foreground text-right">(LKR '000)</TableHead>
                        <TableHead className="font-normal text-xs text-muted-foreground text-right">(LKR '000)</TableHead>
                        <TableHead className="font-normal text-xs text-muted-foreground text-right">(LKR '000)</TableHead>
                        <TableHead className="font-normal text-xs text-muted-foreground text-right">(LKR '000)</TableHead>
                        <TableHead className="font-normal text-xs text-muted-foreground text-right">(LKR '000)</TableHead>
                        <TableHead className="font-normal text-xs text-muted-foreground text-right"></TableHead>
                        <TableHead className="font-normal text-xs text-muted-foreground text-right"></TableHead>
                        <TableHead className="font-normal text-xs text-muted-foreground text-right"></TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {reports.map((report) => (
                        <TableRow key={`${report.year}-${report.quarter}`}>
                            <TableCell style={{ position: 'sticky', left: 0, background: 'white', zIndex: 1, minWidth: 80 }}>{report.quarter}</TableCell>
                            <TableCell style={{ position: 'sticky', left: 80, background: 'white', zIndex: 1, minWidth: 80 }}>{report.year}</TableCell>
                            <TableCell className="text-right">{report.financial_metrics.revenue != null ? (report.financial_metrics.revenue / 1000).toLocaleString() : "N/A"}</TableCell>
                            <TableCell className="text-right">{report.financial_metrics.cost_of_goods_sold != null ? (report.financial_metrics.cost_of_goods_sold / 1000).toLocaleString() : "N/A"}</TableCell>
                            <TableCell className="text-right">{report.financial_metrics.gross_profit != null ? (report.financial_metrics.gross_profit / 1000).toLocaleString() : "N/A"}</TableCell>
                            <TableCell className="text-right">{report.financial_metrics.other_income != null ? (report.financial_metrics.other_income / 1000).toLocaleString() : "N/A"}</TableCell>
                            <TableCell className="text-right">{report.financial_metrics.distribution_costs != null ? (report.financial_metrics.distribution_costs / 1000).toLocaleString() : "N/A"}</TableCell>
                            <TableCell className="text-right">{report.financial_metrics.administrative_expenses != null ? (report.financial_metrics.administrative_expenses / 1000).toLocaleString() : "N/A"}</TableCell>
                            <TableCell className="text-right">{report.financial_metrics.operating_income != null ? (report.financial_metrics.operating_income / 1000).toLocaleString() : "N/A"}</TableCell>
                            <TableCell className="text-right">{report.financial_metrics.finance_costs != null ? (report.financial_metrics.finance_costs / 1000).toLocaleString() : "N/A"}</TableCell>
                            <TableCell className="text-right">{report.financial_metrics.finance_income != null ? (report.financial_metrics.finance_income / 1000).toLocaleString() : "N/A"}</TableCell>
                            <TableCell className="text-right">{report.financial_metrics.share_of_profit_equity_investee != null ? (report.financial_metrics.share_of_profit_equity_investee / 1000).toLocaleString() : "N/A"}</TableCell>
                            <TableCell className="text-right">{report.financial_metrics.profit_before_tax != null ? (report.financial_metrics.profit_before_tax / 1000).toLocaleString() : "N/A"}</TableCell>
                            <TableCell className="text-right">{report.financial_metrics.tax_expense != null ? (report.financial_metrics.tax_expense / 1000).toLocaleString() : "N/A"}</TableCell>
                            <TableCell className="text-right">{report.financial_metrics.net_income != null ? (report.financial_metrics.net_income / 1000).toLocaleString() : "N/A"}</TableCell>
                            <TableCell className="text-right">{report.financial_metrics.eps_basic != null ? report.financial_metrics.eps_basic.toFixed(2) : "N/A"}</TableCell>
                            <TableCell className="text-right">{report.financial_metrics.eps_diluted != null ? report.financial_metrics.eps_diluted.toFixed(2) : "N/A"}</TableCell>
                            <TableCell className="text-right">{report.financial_metrics.dividend_per_share != null ? report.financial_metrics.dividend_per_share.toFixed(2) : "N/A"}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </main>
    );
} 