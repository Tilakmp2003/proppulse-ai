import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown } from "lucide-react";
import { formatCurrency, formatPercent, formatNumber } from "@/lib/utils";

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  changeType?: "percentage" | "number" | "currency";
  format?: "currency" | "percentage" | "number";
  icon?: React.ReactNode;
}

export function MetricCard({
  title,
  value,
  change,
  changeType = "percentage",
  format = "number",
  icon,
}: MetricCardProps) {
  const formatValue = (val: string | number) => {
    if (typeof val === "string") return val;

    switch (format) {
      case "currency":
        return formatCurrency(val);
      case "percentage":
        return formatPercent(val);
      default:
        return formatNumber(val);
    }
  };

  const formatChange = (val: number) => {
    switch (changeType) {
      case "currency":
        return formatCurrency(Math.abs(val));
      case "percentage":
        return formatPercent(Math.abs(val));
      default:
        return formatNumber(Math.abs(val));
    }
  };

  const isPositive = change !== undefined ? change >= 0 : true;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-gray-600">
          {title}
        </CardTitle>
        {icon && <div className="h-4 w-4 text-muted-foreground">{icon}</div>}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{formatValue(value)}</div>
        {change !== undefined && (
          <p className="text-xs text-muted-foreground flex items-center mt-1">
            {isPositive ? (
              <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
            ) : (
              <TrendingDown className="h-4 w-4 text-red-500 mr-1" />
            )}
            <span className={isPositive ? "text-green-500" : "text-red-500"}>
              {isPositive ? "+" : "-"}
              {formatChange(change)}
            </span>
            <span className="ml-1">from last month</span>
          </p>
        )}
      </CardContent>
    </Card>
  );
}
