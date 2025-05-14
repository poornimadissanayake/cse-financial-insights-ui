import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getCompanies, getCompanyFinancials } from "@/lib/api";
import Link from "next/link";
import { CompanyComparisonChart } from "@/components/CompanyComparisonChart";

export default async function Home() {
  const companies = await getCompanies();

  // Fetch financial data for all companies
  const companyData = await Promise.all(
    companies.map(async (company) => {
      const data = await getCompanyFinancials(company.symbol);
      return [company.symbol, data];
    })
  );

  const companyDataMap = Object.fromEntries(companyData);

  return (
    <main className="container mx-auto py-0">
      <h2 className="text-2xl font-semibold mb-1">Overview</h2>
      <div className="flex justify-between items-center mb-2">
        {/* <h1 className="text-4xl font-bold">Financial Dashboard</h1> */}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <CompanyComparisonChart companies={companies} companyData={companyDataMap} />
        </div>
        <div className="flex flex-col gap-8">
          {companies.map((company) => (
            <Link href={`/companies/${company.symbol}`} key={company.symbol}>
              <Card className="hover:bg-accent transition-colors">
                <CardHeader>
                  <CardTitle>{company.symbol}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p>Latest Quarter: {company.latest_quarter} {company.latest_year}</p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </main>
  );
}
