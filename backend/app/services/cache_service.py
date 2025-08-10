import redis.asyncio as redis
import json
import logging
from typing import Optional, Any, Dict
from app.core.config import settings

logger = logging.getLogger(__name__)

class CacheService:
    """Redis 캐시 서비스"""
    
    def __init__(self):
        self.redis_client = None
        self.ttl = settings.REDIS_TTL
    
    async def _get_client(self) -> redis.Redis:
        """Redis 클라이언트 반환"""
        if self.redis_client is None:
            try:
                self.redis_client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True
                )
                # 연결 테스트
                await self.redis_client.ping()
                logger.info("Redis 연결 성공")
            except Exception as e:
                logger.error(f"Redis 연결 실패: {e}")
                # Redis 연결 실패 시 None 반환하여 캐시 비활성화
                return None
        return self.redis_client
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        캐시에서 값 조회
        
        Args:
            key: 캐시 키
            
        Returns:
            캐시된 값 또는 None
        """
        try:
            client = await self._get_client()
            if client is None:
                return None
            
            value = await client.get(key)
            if value:
                return json.loads(value)
            return None
            
        except Exception as e:
            logger.error(f"캐시 조회 실패: {e}")
            return None
    
    async def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        캐시에 값 저장
        
        Args:
            key: 캐시 키
            value: 저장할 값
            ttl: 만료 시간 (초)
            
        Returns:
            저장 성공 여부
        """
        try:
            client = await self._get_client()
            if client is None:
                return False
            
            ttl = ttl or self.ttl
            await client.setex(
                key,
                ttl,
                json.dumps(value, ensure_ascii=False)
            )
            return True
            
        except Exception as e:
            logger.error(f"캐시 저장 실패: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        캐시에서 값 삭제
        
        Args:
            key: 캐시 키
            
        Returns:
            삭제 성공 여부
        """
        try:
            client = await self._get_client()
            if client is None:
                return False
            
            result = await client.delete(key)
            return result > 0
            
        except Exception as e:
            logger.error(f"캐시 삭제 실패: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """
        패턴에 맞는 캐시 키들 삭제
        
        Args:
            pattern: Redis 패턴 (예: "chat:*")
            
        Returns:
            삭제된 키 개수
        """
        try:
            client = await self._get_client()
            if client is None:
                return 0
            
            keys = await client.keys(pattern)
            if keys:
                await client.delete(*keys)
                logger.info(f"패턴 '{pattern}'에 맞는 {len(keys)}개 캐시 삭제")
                return len(keys)
            return 0
            
        except Exception as e:
            logger.error(f"패턴 캐시 삭제 실패: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        캐시 통계 정보 반환
        
        Returns:
            캐시 통계 정보
        """
        try:
            client = await self._get_client()
            if client is None:
                return {"status": "disconnected"}
            
            info = await client.info()
            return {
                "status": "connected",
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0)
            }
            
        except Exception as e:
            logger.error(f"캐시 통계 조회 실패: {e}")
            return {"status": "error", "error": str(e)}
    
    async def close(self):
        """Redis 연결 종료"""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
            logger.info("Redis 연결 종료")
