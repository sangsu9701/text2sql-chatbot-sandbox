"use client";

import { useState } from "react";
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  flexRender,
  type ColumnDef,
  type SortingState,
} from "@tanstack/react-table";
import { ChevronDown, ChevronUp, ChevronsUpDown } from "lucide-react";

interface DataTableProps {
  data: any[];
  columns: string[];
  rowCount: number;
}

export default function DataTable({ data, columns, rowCount }: DataTableProps) {
  const [sorting, setSorting] = useState<SortingState>([]);

  // 컬럼 정의 생성
  const tableColumns: ColumnDef<any>[] = columns.map((column) => ({
    accessorKey: column,
    header: column,
    cell: ({ getValue }) => {
      const value = getValue();
      // 숫자 형식 포맷팅
      if (typeof value === 'number') {
        return value.toLocaleString();
      }
      return value;
    },
  }));

  const table = useReactTable({
    data,
    columns: tableColumns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onSortingChange: setSorting,
    state: {
      sorting,
    },
    initialState: {
      pagination: {
        pageSize: 10,
      },
    },
  });

  const getSortIcon = (column: any) => {
    if (!column.getCanSort()) return null;
    
    const isSorted = column.getIsSorted();
    if (isSorted === "asc") {
      return <ChevronUp className="w-4 h-4" />;
    }
    if (isSorted === "desc") {
      return <ChevronDown className="w-4 h-4" />;
    }
    return <ChevronsUpDown className="w-4 h-4" />;
  };

  return (
    <div className="w-full">
      {/* 테이블 */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    className="px-4 py-3 text-left font-medium text-gray-700 cursor-pointer hover:bg-gray-100"
                    onClick={header.column.getToggleSortingHandler()}
                  >
                    <div className="flex items-center space-x-1">
                      <span>{flexRender(header.column.columnDef.header, header.getContext())}</span>
                      {getSortIcon(header.column)}
                    </div>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row) => (
              <tr key={row.id} className="border-b hover:bg-gray-50">
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="px-4 py-3 text-gray-900">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 페이지네이션 */}
      {rowCount > 10 && (
        <div className="flex items-center justify-between px-4 py-3 bg-gray-50 border-t">
          <div className="text-sm text-gray-700">
            총 {rowCount}개 행 중 {table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1}-
            {Math.min((table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize, rowCount)}개 표시
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
              className="px-3 py-1 text-sm border rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
            >
              이전
            </button>
            <span className="text-sm text-gray-700">
              {table.getState().pagination.pageIndex + 1} / {table.getPageCount()}
            </span>
            <button
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
              className="px-3 py-1 text-sm border rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
            >
              다음
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
