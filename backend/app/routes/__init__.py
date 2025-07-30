"""
Route modülleri için paket.
Tüm API endpoint'leri için modüller içerir.
"""

from .common import create_tables_if_needed, get_db
from .orders import router as orders_router
from .stocks import router as stocks_router
from .users import router as users_router

# Ana router'ı export et
router = users_router
