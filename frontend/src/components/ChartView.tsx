"use client";

import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface ChartViewProps {
  data: any[];
  columns: string[];
  chartType: string;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

export default function ChartView({ data, columns, chartType }: ChartViewProps) {
  // 차트 데이터 준비
  const prepareChartData = () => {
    if (data.length === 0) return [];

    // 첫 번째 컬럼을 카테고리로, 두 번째 컬럼을 값으로 사용
    const categoryCol = columns[0];
    const valueCol = columns[1];

    return data.map((row, index) => ({
      name: row[categoryCol] || `항목 ${index + 1}`,
      value: typeof row[valueCol] === 'number' ? row[valueCol] : 0,
      [categoryCol]: row[categoryCol],
      [valueCol]: row[valueCol],
    }));
  };

  const chartData = prepareChartData();

  const renderChart = () => {
    switch (chartType) {
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value) => [value.toLocaleString(), '값']} />
              <Legend />
              <Bar dataKey="value" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'line':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value) => [value.toLocaleString(), '값']} />
              <Legend />
              <Line type="monotone" dataKey="value" stroke="#8884d8" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        );

      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [value.toLocaleString(), '값']} />
            </PieChart>
          </ResponsiveContainer>
        );

      default:
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value) => [value.toLocaleString(), '값']} />
              <Legend />
              <Bar dataKey="value" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        );
    }
  };

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        표시할 데이터가 없습니다.
      </div>
    );
  }

  return (
    <div className="p-4">
      {renderChart()}
    </div>
  );
}
