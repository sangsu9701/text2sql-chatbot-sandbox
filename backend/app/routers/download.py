from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Dict, Any
import pandas as pd
import io
import logging
import xlsxwriter

from app.core.database import get_db
from app.models.schemas import DownloadRequest
from app.services.sql_guardrails import SQLGuardrails

logger = logging.getLogger(__name__)

router = APIRouter()
guardrails = SQLGuardrails()

@router.post("/download/xlsx")
async def download_xlsx(
    request: DownloadRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    SQL 쿼리 결과를 XLSX 파일로 다운로드
    """
    try:
        # SQL 검증
        validated_sql = await guardrails.validate_and_clean_sql(request.sql)
        
        # 쿼리 실행
        result = await session.execute(text(validated_sql))
        rows = [dict(row._mapping) for row in result.fetchall()]
        columns = list(result.keys()) if result.keys() else []
        
        if not rows:
            raise HTTPException(
                status_code=404,
                detail="다운로드할 데이터가 없습니다"
            )
        
        # DataFrame 생성
        df = pd.DataFrame(rows)
        
        # XLSX 파일 생성
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Data', index=False)
            
            # 워크시트 가져오기
            worksheet = writer.sheets['Data']
            workbook = writer.book
            
            # 헤더 스타일 설정
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })
            
            # 데이터 스타일 설정
            data_format = workbook.add_format({
                'text_wrap': True,
                'valign': 'top',
                'border': 1
            })
            
            # 헤더에 스타일 적용
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # 데이터에 스타일 적용
            for row_num in range(len(df)):
                for col_num in range(len(df.columns)):
                    worksheet.write(row_num + 1, col_num, df.iloc[row_num, col_num], data_format)
            
            # 컬럼 너비 자동 조정
            for i, col in enumerate(df.columns):
                max_len = max(
                    df[col].astype(str).map(len).max(),
                    len(str(col))
                )
                worksheet.set_column(i, i, min(max_len + 2, 50))
        
        output.seek(0)
        
        # 파일명 생성
        filename = f"snop_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        logger.info(f"XLSX 다운로드 완료: {filename}")
        
        return StreamingResponse(
            io.BytesIO(output.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except ValueError as e:
        logger.error(f"SQL 검증 실패: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"SQL 검증 실패: {str(e)}"
        )
    except Exception as e:
        logger.error(f"XLSX 다운로드 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"다운로드 실패: {str(e)}"
        )

@router.post("/download/csv")
async def download_csv(
    request: DownloadRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    SQL 쿼리 결과를 CSV 파일로 다운로드
    """
    try:
        # SQL 검증
        validated_sql = await guardrails.validate_and_clean_sql(request.sql)
        
        # 쿼리 실행
        result = await session.execute(text(validated_sql))
        rows = [dict(row._mapping) for row in result.fetchall()]
        columns = list(result.keys()) if result.keys() else []
        
        if not rows:
            raise HTTPException(
                status_code=404,
                detail="다운로드할 데이터가 없습니다"
            )
        
        # DataFrame 생성
        df = pd.DataFrame(rows)
        
        # CSV 파일 생성
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        
        # 파일명 생성
        filename = f"snop_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        logger.info(f"CSV 다운로드 완료: {filename}")
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except ValueError as e:
        logger.error(f"SQL 검증 실패: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"SQL 검증 실패: {str(e)}"
        )
    except Exception as e:
        logger.error(f"CSV 다운로드 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"다운로드 실패: {str(e)}"
        )
