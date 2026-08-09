from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field
from pydantic import ConfigDict


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)


class LoginResponse(BaseModel):
    token: str
    role: str
    name: str


class BookBase(BaseModel):
    ma: str = Field(..., min_length=1, max_length=20)
    ten: str = Field(..., min_length=1, max_length=255)
    tacGia: str = Field(..., min_length=1, max_length=255)
    theLoai: str = Field(..., min_length=1, max_length=100)
    nxb: str = Field(..., min_length=1, max_length=255)
    namXb: int = Field(..., ge=1000, le=2100)
    soLuong: int = Field(..., ge=0)
    theLoaiId: str | None = Field(None, max_length=20)
    nxbId: str | None = Field(None, max_length=20)


class LibraryConfigOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    max_borrow_days: int
    overdue_fine_per_day: float
    max_books_at_once: int


class LibraryConfigUpdate(BaseModel):
    max_borrow_days: int = Field(..., ge=1, le=365)
    overdue_fine_per_day: float = Field(..., ge=0)
    max_books_at_once: int = Field(..., ge=1, le=100)


class AIConfigOut(BaseModel):
    provider: str
    model: str
    api_key_masked: str
    has_api_key: bool
    prompt_template: str


class AIConfigUpdate(BaseModel):
    provider: str | None = Field(None, max_length=50)
    model: str | None = Field(None, max_length=100)
    api_key: str | None = Field(None, max_length=500)
    prompt_template: str | None = None


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str | None
    role: str | None
    action: str
    entity: str
    entity_id: str | None
    details: str | None
    created_at: datetime


class BackupOut(BaseModel):
    message: str
    path: str


class ReaderCreate(BaseModel):
    ma: str = Field(..., min_length=1, max_length=20)
    hoTen: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., min_length=1, max_length=255)
    soDienThoai: str = Field(..., min_length=1, max_length=20)
    loaiDocGia: Literal["sinh_vien", "giang_vien", "khac"]
    trangThaiThe: Literal["hoat_dong", "khoa"] = "hoat_dong"


class ReaderUpdate(BaseModel):
    hoTen: str | None = Field(None, min_length=1, max_length=255)
    email: str | None = Field(None, min_length=1, max_length=255)
    soDienThoai: str | None = Field(None, min_length=1, max_length=20)
    loaiDocGia: Literal["sinh_vien", "giang_vien", "khac"] | None = None
    trangThaiThe: Literal["hoat_dong", "khoa"] | None = None


class ReaderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ma: str
    hoTen: str
    email: str
    soDienThoai: str
    loaiDocGia: str
    trangThaiThe: str
    ngayTao: datetime


class BorrowItemCreate(BaseModel):
    ma_sach: str = Field(..., min_length=1, max_length=20)
    so_luong: int = Field(..., ge=1)


class BorrowCreate(BaseModel):
    ma_phieu: str = Field(..., min_length=1, max_length=20)
    ma_doc_gia: str = Field(..., min_length=1, max_length=20)
    items: list[BorrowItemCreate] = Field(..., min_length=1)


class BorrowDetailOut(BaseModel):
    ma_sach: str
    so_luong: int
    ngay_tra_chi_tiet: datetime | None


class FineOut(BaseModel):
    so_ngay_qua_han: int
    so_tien: float
    da_thu: bool = False
    ngay_thu: datetime | None = None


class BorrowSlipOut(BaseModel):
    ma_phieu: str
    ma_doc_gia: str
    ngay_muon: datetime
    han_tra: datetime
    ngay_tra: datetime | None
    trang_thai: str
    so_lan_gia_han: int
    details: list[BorrowDetailOut]
    fines: list[FineOut] = Field(default_factory=list)


class BorrowReturnOut(BaseModel):
    message: str
    ngay_tra: datetime
    fine: FineOut | None = None


class BorrowRenewOut(BaseModel):
    message: str
    han_tra_moi: datetime
    so_lan_gia_han: int
    fine: FineOut | None = None


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)
    hoTen: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., min_length=1, max_length=255)
    soDienThoai: str = Field(..., min_length=1, max_length=20)
    loaiDocGia: Literal["sinh_vien", "giang_vien", "khac"] = "sinh_vien"


class RegisterResponse(BaseModel):
    token: str
    role: str
    name: str
    reader_ma: str


class BorrowHistoryOut(BaseModel):
    ma_phieu: str
    ma_doc_gia: str
    ngay_muon: datetime
    han_tra: datetime
    ngay_tra: datetime | None
    trang_thai: str
    so_lan_gia_han: int
    details: list[BorrowDetailOut]
    fines: list[FineOut]


class RequestCreate(BaseModel):
    ma_yeu_cau: str = Field(..., min_length=1, max_length=18)
    loai: Literal["MUON", "TRA", "GIA_HAN"]
    ma_phieu: str | None = Field(None, min_length=1, max_length=20)
    items: list[BorrowItemCreate] | None = None


class RequestOut(BaseModel):
    ma_yeu_cau: str
    loai: str
    ma_doc_gia: str
    ma_phieu: str | None
    items: list[BorrowItemCreate]
    trang_thai: str
    ngay_tao: datetime


class AccountCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)
    ho_ten: str = Field(..., min_length=1, max_length=255)
    role: Literal["librarian", "reader"]
    reader_id: str | None = Field(None, max_length=20)


class AccountUpdate(BaseModel):
    ho_ten: str | None = Field(None, min_length=1, max_length=255)
    password: str | None = Field(None, min_length=6, max_length=128)
    is_active: bool | None = None
    role: Literal["librarian", "reader"] | None = None
    reader_id: str | None = None


class AccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    ho_ten: str
    role: str
    is_active: bool
    reader_id: str | None
    created_at: datetime


class CategoryCreate(BaseModel):
    ma: str = Field(..., min_length=1, max_length=20)
    ten: str = Field(..., min_length=1, max_length=100)


class CategoryUpdate(BaseModel):
    ten: str = Field(..., min_length=1, max_length=100)


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ma: str
    ten: str


class NxbCreate(BaseModel):
    ma: str = Field(..., min_length=1, max_length=20)
    ten: str = Field(..., min_length=1, max_length=255)


class NxbUpdate(BaseModel):
    ten: str = Field(..., min_length=1, max_length=255)


class NxbOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ma: str
    ten: str


class RestoreRequest(BaseModel):
    file_path: str = Field(..., min_length=1, max_length=500)


class ReservationCreate(BaseModel):
    ma_sach: str = Field(..., min_length=1, max_length=20)
    ma_doc_gia: str | None = Field(None, max_length=20)


class ReservationOut(BaseModel):
    ma_dat: str
    ma_sach: str
    ten_sach: str
    ma_doc_gia: str
    ngay_dat: datetime
    trang_thai: str


class NotificationOut(BaseModel):
    id: str
    loai: Literal["SAP_HET_HAN", "QUA_HAN", "SACH_SAN_SANG"]
    noi_dung: str
    ngay: datetime
    da_doc: bool


class CollectFineOut(BaseModel):
    message: str
    so_tien_da_thu: float
    ngay_thu: datetime


class StatsBookOut(BaseModel):
    ma_sach: str
    ten_sach: str
    so_lan_muon: int


class StatsReaderOut(BaseModel):
    ma_doc_gia: str
    ho_ten: str
    so_phieu_muon: int


class StatsOverdueOut(BaseModel):
    ma_phieu: str
    ma_sach: str
    ten_sach: str
    ma_doc_gia: str
    ho_ten: str
    so_ngay_qua_han: int
