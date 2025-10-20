"""
Language Configuration for YVM ERP System
다국어 지원: 한국어(KO), 영어(EN), 베트남어(VN), 태국어(TH)
"""

# 지원 언어
SUPPORTED_LANGUAGES = {
    'KO': '한국어',
    'EN': 'English',
    'VN': 'Tiếng Việt',
    'TH': 'ภาษาไทย'
}

# 언어별 라벨 매핑
LANGUAGE_LABELS = {
    # Customer Section
    'customer': {
        'KO': '고객사',
        'EN': 'Customer',
        'VN': 'Khách hàng',
        'TH': 'ลูกค้า'
    },
    'delivery_to': {
        'KO': '납품처',
        'EN': 'Delivery To',
        'VN': 'Giao đến',
        'TH': 'จัดส่งถึง'
    },
    'project_name': {
        'KO': '프로젝트명',
        'EN': 'Project Name',
        'VN': 'Tên dự án',
        'TH': 'ชื่อโครงการ'
    },
    'part_name': {
        'KO': '품명',
        'EN': 'Part Name',
        'VN': 'Tên chi tiết',
        'TH': 'ชื่อชิ้นส่วน'
    },
    'mold_no': {
        'KO': '금형번호',
        'EN': 'Mold No.',
        'VN': 'Số khuôn',
        'TH': 'หมายเลขแม่พิมพ์'
    },
    'ymv_no': {
        'KO': 'YMV 번호',
        'EN': 'YMV No.',
        'VN': 'Số YMV',
        'TH': 'หมายเลข YMV'
    },
    'sales_contact': {
        'KO': '영업담당',
        'EN': 'Sales Contact',
        'VN': 'Người liên hệ',
        'TH': 'ผู้ติดต่อฝ่ายขาย'
    },
    'injection_ton': {
        'KO': '사출기 톤수',
        'EN': 'Injection Ton',
        'VN': 'Tấn ép',
        'TH': 'ตันเครื่องฉีด'
    },
    'resin': {
        'KO': '수지',
        'EN': 'Resin',
        'VN': 'Nhựa',
        'TH': 'เรซิน'
    },
    'additive': {
        'KO': '첨가제',
        'EN': 'Additive',
        'VN': 'Phụ gia',
        'TH': 'สารเติมแต่ง'
    },
    'color_change': {
        'KO': '색상 변경',
        'EN': 'Color Change',
        'VN': 'Đổi màu',
        'TH': 'เปลี่ยนสี'
    },
    'order_type': {
        'KO': '주문 유형',
        'EN': 'Order Type',
        'VN': 'Loại đơn hàng',
        'TH': 'ประเภทคำสั่งซื้อ'
    },
    'customer_entry_mode': {
        'KO': '고객 입력 방식',
        'EN': 'Customer Entry Mode',
        'VN': 'Chế độ nhập khách hàng',
        'TH': 'โหมดการป้อนข้อมูลลูกค้า'
    },
    'select_existing': {
        'KO': '기존 고객 선택',
        'EN': 'Select Existing',
        'VN': 'Chọn có sẵn',
        'TH': 'เลือกที่มีอยู่'
    },
    'new_customer': {
        'KO': '신규 고객',
        'EN': 'New Customer',
        'VN': 'Khách hàng mới',
        'TH': 'ลูกค้าใหม่'
    },
    
    # Base Section
    'base': {
        'KO': '베이스',
        'EN': 'BASE',
        'VN': 'ĐẾ',
        'TH': 'ฐาน'
    },
    'plate': {
        'KO': '플레이트',
        'EN': 'PLATE',
        'VN': 'TẤM',
        'TH': 'แผ่น'
    },
    'top': {
        'KO': '상부',
        'EN': 'TOP',
        'VN': 'TRÊN',
        'TH': 'ด้านบน'
    },
    'space': {
        'KO': '간격',
        'EN': 'SPACE',
        'VN': 'KHOẢNG',
        'TH': 'ช่องว่าง'
    },
    'holding': {
        'KO': '홀딩',
        'EN': 'HOLDING',
        'VN': 'GIỮ',
        'TH': 'จับยึด'
    },
    'width': {
        'KO': '폭',
        'EN': 'Width',
        'VN': 'Rộng',
        'TH': 'ความกว้าง'
    },
    'length': {
        'KO': '길이',
        'EN': 'Length',
        'VN': 'Dài',
        'TH': 'ความยาว'
    },
    'height': {
        'KO': '높이',
        'EN': 'Height',
        'VN': 'Cao',
        'TH': 'ความสูง'
    },
    'base_processor': {
        'KO': '베이스 가공업체',
        'EN': 'BASE Processor',
        'VN': 'Nhà sản xuất đế',
        'TH': 'ผู้ประมวลผลฐาน'
    },
    'cooling_pt_tap': {
        'KO': '냉각 PT/TAP',
        'EN': 'Cooling PT/TAP',
        'VN': 'Làm mát PT/TAP',
        'TH': 'การระบายความร้อน PT/TAP'
    },
    'base_dimensions': {
        'KO': '베이스 치수',
        'EN': 'BASE Dimensions',
        'VN': 'Kích thước đế',
        'TH': 'ขนาดฐาน'
    },
    'dimensions_table': {
        'KO': '치수 테이블',
        'EN': 'Dimensions Table',
        'VN': 'Bảng kích thước',
        'TH': 'ตารางขนาด'
    },
    'part': {
        'KO': '부품',
        'EN': 'Part',
        'VN': 'Phần',
        'TH': 'ส่วน'
    },
    
    # Nozzle Section
    'nozzle': {
        'KO': '노즐',
        'EN': 'NOZZLE',
        'VN': 'VÒI PHUN',
        'TH': 'หัวฉีด'
    },
    'nozzle_type': {
        'KO': '노즐 타입',
        'EN': 'Nozzle Type',
        'VN': 'Loại vòi phun',
        'TH': 'ประเภทหัวฉีด'
    },
    'gate_close': {
        'KO': '게이트 닫힘',
        'EN': 'Gate Close',
        'VN': 'Đóng cổng',
        'TH': 'ปิดเกต'
    },
    'qty': {
        'KO': '수량',
        'EN': 'QTY',
        'VN': 'SL',
        'TH': 'จำนวน'
    },
    'quantity': {
        'KO': '수량',
        'EN': 'Quantity',
        'VN': 'Số lượng',
        'TH': 'จำนวน'
    },
    'ht_type': {
        'KO': 'H/T 타입',
        'EN': 'H/T Type',
        'VN': 'Loại H/T',
        'TH': 'ประเภท H/T'
    },
    'nozzle_length': {
        'KO': '노즐 길이',
        'EN': 'Nozzle Length',
        'VN': 'Chiều dài vòi phun',
        'TH': 'ความยาวหัวฉีด'
    },
    'nozzle_specifications': {
        'KO': '노즐 사양',
        'EN': 'NOZZLE Specifications',
        'VN': 'Thông số vòi phun',
        'TH': 'ข้อกำหนดหัวฉีด'
    },
    'type': {
        'KO': '타입',
        'EN': 'Type',
        'VN': 'Loại',
        'TH': 'ประเภท'
    },
    
    # Manifold Section
    'manifold': {
        'KO': '매니폴드',
        'EN': 'MANIFOLD',
        'VN': 'ỐNG DẪN',
        'TH': 'ท่อร่วม'
    },
    'manifold_type': {
        'KO': '매니폴드 타입',
        'EN': 'Manifold Type',
        'VN': 'Loại ống dẫn',
        'TH': 'ประเภทท่อร่วม'
    },
    'manifold_standard': {
        'KO': '매니폴드 표준',
        'EN': 'Manifold Standard',
        'VN': 'Tiêu chuẩn ống dẫn',
        'TH': 'มาตรฐานท่อร่วม'
    },
    'manifold_ht_type': {
        'KO': '매니폴드 H/T 타입',
        'EN': 'Manifold H/T Type',
        'VN': 'Loại H/T ống dẫn',
        'TH': 'ประเภท H/T ท่อร่วม'
    },
    'manifold_specifications': {
        'KO': '매니폴드 사양',
        'EN': 'MANIFOLD Specifications',
        'VN': 'Thông số ống dẫn',
        'TH': 'ข้อกำหนดท่อร่วม'
    },
    
    # Cylinder Section
    'cylinder': {
        'KO': '실린더',
        'EN': 'CYLINDER',
        'VN': 'XI LANH',
        'TH': 'กระบอกสูบ'
    },
    'cylinder_type': {
        'KO': '실린더 타입',
        'EN': 'Cylinder Type',
        'VN': 'Loại xi lanh',
        'TH': 'ประเภทกระบอกสูบ'
    },
    'cylinder_sensor': {
        'KO': '실린더 & 센서',
        'EN': 'CYLINDER & SENSOR',
        'VN': 'XI LANH & CẢM BIẾN',
        'TH': 'กระบอกสูบและเซ็นเซอร์'
    },
    
    # Sensor Section
    'sensor': {
        'KO': '센서',
        'EN': 'SENSOR',
        'VN': 'CẢM BIẾN',
        'TH': 'เซ็นเซอร์'
    },
    'sensor_type': {
        'KO': '센서 타입',
        'EN': 'Sensor Type',
        'VN': 'Loại cảm biến',
        'TH': 'ประเภทเซ็นเซอร์'
    },
    
    # Timer Connector
    'timer_connector': {
        'KO': '타이머 커넥터',
        'EN': 'TIMER CONNECTOR',
        'VN': 'ĐẦU NỐI BỘ ĐẾM',
        'TH': 'ตัวเชื่อมต่อตัวจับเวลา'
    },
    'timer_and_connector': {
        'KO': '타이머 & 커넥터',
        'EN': 'TIMER & CONNECTOR',
        'VN': 'BỘ ĐẾM & ĐẦU NỐI',
        'TH': 'ตัวจับเวลาและตัวเชื่อมต่อ'
    },
    'sol_volt': {
        'KO': 'SOL 전압',
        'EN': 'SOL Voltage',
        'VN': 'ĐIỆN ÁP SOL',
        'TH': 'แรงดันไฟฟ้า SOL'
    },
    'sol_control': {
        'KO': 'SOL 제어',
        'EN': 'SOL Control',
        'VN': 'Điều khiển SOL',
        'TH': 'การควบคุม SOL'
    },
    'pin_type': {
        'KO': 'PIN 타입',
        'EN': 'PIN Type',
        'VN': 'Loại PIN',
        'TH': 'ประเภท PIN'
    },
    'con_type': {
        'KO': 'CON 타입',
        'EN': 'CON Type',
        'VN': 'Loại CON',
        'TH': 'ประเภท CON'
    },
    'buried': {
        'KO': '매립',
        'EN': 'BURIED',
        'VN': 'CHÔN',
        'TH': 'ฝังใต้ดิน'
    },
    'location': {
        'KO': '위치',
        'EN': 'Location',
        'VN': 'Vị trí',
        'TH': 'ตำแหน่ง'
    },
    'individual': {
        'KO': '개별',
        'EN': 'Individual',
        'VN': 'Riêng lẻ',
        'TH': 'แยกเดี่ยว'
    },
    'integrated': {
        'KO': '통합',
        'EN': 'Integrated',
        'VN': 'Tích hợp',
        'TH': 'รวม'
    },
    
    # Heater Connector
    'heater_connector': {
        'KO': '히터 커넥터',
        'EN': 'HEATER CONNECTOR',
        'VN': 'ĐẦU NỐI NHIỆT',
        'TH': 'ตัวเชื่อมต่อฮีตเตอร์'
    },
    
    # ID Card
    'id_card': {
        'KO': 'ID 카드',
        'EN': 'ID CARD',
        'VN': 'THẺ ID',
        'TH': 'บัตรประจำตัว'
    },
    'id_card_type': {
        'KO': 'ID 카드 타입',
        'EN': 'ID Card Type',
        'VN': 'Loại thẻ ID',
        'TH': 'ประเภทบัตรประจำตัว'
    },
    'domestic': {
        'KO': '국내',
        'EN': 'Domestic',
        'VN': 'Trong nước',
        'TH': 'ภายในประเทศ'
    },
    'global': {
        'KO': '글로벌',
        'EN': 'Global',
        'VN': 'Toàn cầu',
        'TH': 'ระดับโลก'
    },
    
    # NL
    'nl': {
        'KO': 'NL',
        'EN': 'NL',
        'VN': 'NL',
        'TH': 'NL'
    },
    'nl_phi': {
        'KO': 'NL Φ',
        'EN': 'NL Φ',
        'VN': 'NL Φ',
        'TH': 'NL Φ'
    },
    'nl_sr': {
        'KO': 'NL S/R',
        'EN': 'NL S/R',
        'VN': 'NL S/R',
        'TH': 'NL S/R'
    },
    'locate_ring': {
        'KO': '로케이트 링',
        'EN': 'LOCATE RING',
        'VN': 'VÒNG ĐỊNH VỊ',
        'TH': 'วงแหวนตำแหน่ง'
    },
    'nl_information': {
        'KO': 'NL 정보',
        'EN': 'NL Information',
        'VN': 'Thông tin NL',
        'TH': 'ข้อมูล NL'
    },
    
    # Gate Section
    'gate': {
        'KO': '게이트',
        'EN': 'GATE',
        'VN': 'CỔNG',
        'TH': 'เกต'
    },
    'gate_phi': {
        'KO': 'GATE Φ',
        'EN': 'GATE Φ',
        'VN': 'CỔNG Φ',
        'TH': 'เกต Φ'
    },
    'gate_length': {
        'KO': '게이트 길이',
        'EN': 'Gate Length',
        'VN': 'Chiều dài cổng',
        'TH': 'ความยาวเกต'
    },
    'gate_information': {
        'KO': 'GATE 정보',
        'EN': 'GATE Information',
        'VN': 'Thông tin CỔNG',
        'TH': 'ข้อมูลเกต'
    },
    'preview_table': {
        'KO': '미리보기 테이블',
        'EN': 'Preview Table',
        'VN': 'Bảng xem trước',
        'TH': 'ตารางแสดงตัวอย่าง'
    },
    
    # Additional
    'spare_list': {
        'KO': '예비 부품 목록',
        'EN': 'SPARE LIST',
        'VN': 'DANH SÁCH PHỤ TÙNG',
        'TH': 'รายการอะไหล่'
    },
    'special_notes': {
        'KO': '특이사항',
        'EN': 'Special Notes',
        'VN': 'Ghi chú đặc biệt',
        'TH': 'หมายเหตุพิเศษ'
    },
    'additional_information': {
        'KO': '추가 정보',
        'EN': 'Additional Information',
        'VN': 'Thông tin bổ sung',
        'TH': 'ข้อมูลเพิ่มเติม'
    },
    
    # Actions
    'save': {
        'KO': '저장',
        'EN': 'Save',
        'VN': 'Lưu',
        'TH': 'บันทึก'
    },
    'cancel': {
        'KO': '취소',
        'EN': 'Cancel',
        'VN': 'Hủy',
        'TH': 'ยกเลิก'
    },
    'print': {
        'KO': '인쇄',
        'EN': 'Print',
        'VN': 'In',
        'TH': 'พิมพ์'
    },
    'download': {
        'KO': '다운로드',
        'EN': 'Download',
        'VN': 'Tải xuống',
        'TH': 'ดาวน์โหลด'
    },
    'search': {
        'KO': '검색',
        'EN': 'Search',
        'VN': 'Tìm kiếm',
        'TH': 'ค้นหา'
    },
    'edit': {
        'KO': '수정',
        'EN': 'Edit',
        'VN': 'Sửa',
        'TH': 'แก้ไข'
    },
    'delete': {
        'KO': '삭제',
        'EN': 'Delete',
        'VN': 'Xóa',
        'TH': 'ลบ'
    },
    'submit': {
        'KO': '제출',
        'EN': 'Submit',
        'VN': 'Gửi',
        'TH': 'ส่ง'
    },
    'approve': {
        'KO': '승인',
        'EN': 'Approve',
        'VN': 'Phê duyệt',
        'TH': 'อนุมัติ'
    },
    'reject': {
        'KO': '반려',
        'EN': 'Reject',
        'VN': 'Từ chối',
        'TH': 'ปฏิเสธ'
    },
    'back': {
        'KO': '돌아가기',
        'EN': 'Back',
        'VN': 'Quay lại',
        'TH': 'กลับ'
    },
    'preview': {
        'KO': '미리보기',
        'EN': 'Preview',
        'VN': 'Xem trước',
        'TH': 'แสดงตัวอย่าง'
    },
    'reset': {
        'KO': '초기화',
        'EN': 'Reset',
        'VN': 'Đặt lại',
        'TH': 'รีเซ็ต'
    },
    
    # Status
    'draft': {
        'KO': '임시저장',
        'EN': 'Draft',
        'VN': 'Bản nháp',
        'TH': 'ร่าง'
    },
    'submitted': {
        'KO': '제출됨',
        'EN': 'Submitted',
        'VN': 'Đã gửi',
        'TH': 'ส่งแล้ว'
    },
    'approved': {
        'KO': '승인됨',
        'EN': 'Approved',
        'VN': 'Đã duyệt',
        'TH': 'อนุมัติแล้ว'
    },
    'rejected': {
        'KO': '반려됨',
        'EN': 'Rejected',
        'VN': 'Bị từ chối',
        'TH': 'ถูกปฏิเสธ'
    },
    'completed': {
        'KO': '완료',
        'EN': 'Completed',
        'VN': 'Hoàn thành',
        'TH': 'เสร็จสมบูรณ์'
    },
    'status': {
        'KO': '상태',
        'EN': 'Status',
        'VN': 'Trạng thái',
        'TH': 'สถานะ'
    },
    
    # Messages
    'required_field': {
        'KO': '필수 입력',
        'EN': 'Required',
        'VN': 'Bắt buộc',
        'TH': 'จำเป็น'
    },
    'no_data': {
        'KO': '데이터 없음',
        'EN': 'No data',
        'VN': 'Không có dữ liệu',
        'TH': 'ไม่มีข้อมูล'
    },
    'success': {
        'KO': '성공',
        'EN': 'Success',
        'VN': 'Thành công',
        'TH': 'สำเร็จ'
    },
    'error': {
        'KO': '오류',
        'EN': 'Error',
        'VN': 'Lỗi',
        'TH': 'ข้อผิดพลาด'
    },
    'loading': {
        'KO': '로딩 중...',
        'EN': 'Loading...',
        'VN': 'Đang tải...',
        'TH': 'กำลังโหลด...'
    },
    
    # Titles
    'new_specification': {
        'KO': '신규 규격 결정서',
        'EN': 'New Specification',
        'VN': 'Thông số kỹ thuật mới',
        'TH': 'ข้อกำหนดใหม่'
    },
    'specification_list': {
        'KO': '규격 결정서 목록',
        'EN': 'Specification List',
        'VN': 'Danh sách thông số',
        'TH': 'รายการข้อกำหนด'
    },
    'search_and_edit': {
        'KO': '검색 및 수정',
        'EN': 'Search & Edit',
        'VN': 'Tìm kiếm & Sửa',
        'TH': 'ค้นหาและแก้ไข'
    },
    'customer_and_project': {
        'KO': '고객 및 프로젝트 정보',
        'EN': 'Customer & Project Information',
        'VN': 'Thông tin khách hàng & dự án',
        'TH': 'ข้อมูลลูกค้าและโครงการ'
    },
    'base_information': {
        'KO': '베이스 정보',
        'EN': 'BASE Information',
        'VN': 'Thông tin đế',
        'TH': 'ข้อมูลฐาน'
    },
    'technical_specifications': {
        'KO': '기술 사양',
        'EN': 'Technical Specifications',
        'VN': 'Thông số kỹ thuật',
        'TH': 'ข้อกำหนดทางเทคนิค'
    },
    'order_options': {
        'KO': '주문 옵션',
        'EN': 'Order Options',
        'VN': 'Tùy chọn đơn hàng',
        'TH': 'ตัวเลือกคำสั่งซื้อ'
    },
    'link_to_quotation': {
        'KO': '견적서 연결',
        'EN': 'Link to Quotation',
        'VN': 'Liên kết báo giá',
        'TH': 'เชื่อมโยงกับใบเสนอราคา'
    },
    'optional': {
        'KO': '선택사항',
        'EN': 'Optional',
        'VN': 'Tùy chọn',
        'TH': 'ไม่บังคับ'
    },
    'select_quotation': {
        'KO': '견적서 선택',
        'EN': 'Select Quotation',
        'VN': 'Chọn báo giá',
        'TH': 'เลือกใบเสนอราคา'
    },
    'none_manual_entry': {
        'KO': '없음 - 수동 입력',
        'EN': 'None - Manual Entry',
        'VN': 'Không - Nhập thủ công',
        'TH': 'ไม่มี - ป้อนด้วยตนเอง'
    },
    'no_approved_quotations': {
        'KO': '승인된 견적서 없음',
        'EN': 'No approved quotations available',
        'VN': 'Không có báo giá được phê duyệt',
        'TH': 'ไม่มีใบเสนอราคาที่ได้รับการอนุมัติ'
    },
    'refer_to_diagram': {
        'KO': '다이어그램 참조',
        'EN': 'Refer to diagram',
        'VN': 'Tham khảo sơ đồ',
        'TH': 'อ้างอิงไดอะแกรม'
    },
    'refer_to_nozzle_height': {
        'KO': '노즐 높이 다이어그램 참조',
        'EN': 'Refer to nozzle height diagram',
        'VN': 'Tham khảo sơ đồ chiều cao vòi phun',
        'TH': 'อ้างอิงแผนภาพความสูงหัวฉีด'
    },
    'sheath_heater': {
        'KO': '시스 히터',
        'EN': 'Sheath Heater',
        'VN': 'Máy sưởi vỏ bọc',
        'TH': 'ฮีตเตอร์แบบหุ้ม'
    },
    'fixed': {
        'KO': '고정',
        'EN': 'Fixed',
        'VN': 'Cố định',
        'TH': 'คงที่'
    },
    
    # Common terms
    'yes': {
        'KO': '예',
        'EN': 'YES',
        'VN': 'CÓ',
        'TH': 'ใช่'
    },
    'no': {
        'KO': '아니오',
        'EN': 'NO',
        'VN': 'KHÔNG',
        'TH': 'ไม่'
    },
    'all': {
        'KO': '전체',
        'EN': 'All',
        'VN': 'Tất cả',
        'TH': 'ทั้งหมด'
    },
    'total': {
        'KO': '합계',
        'EN': 'Total',
        'VN': 'Tổng cộng',
        'TH': 'รวม'
    },
    'language': {
        'KO': '언어',
        'EN': 'Language',
        'VN': 'Ngôn ngữ',
        'TH': 'ภาษา'
    },
    'output_language': {
        'KO': '출력 언어',
        'EN': 'Output Language',
        'VN': 'Ngôn ngữ đầu ra',
        'TH': 'ภาษาที่แสดงผล'
    },
}


def get_label(key, language='EN'):
    """
    언어별 라벨 반환
    
    Args:
        key (str): 라벨 키
        language (str): 언어 코드 ('KO', 'EN', 'VN', 'TH')
    
    Returns:
        str: 해당 언어의 라벨 (없으면 키 그대로 반환)
    """
    # 언어 코드 정규화 (대문자로 변환)
    language = language.upper()
    
    # 지원하지 않는 언어면 영어로 기본 설정
    if language not in SUPPORTED_LANGUAGES:
        language = 'EN'
    
    if key in LANGUAGE_LABELS:
        return LANGUAGE_LABELS[key].get(language, LANGUAGE_LABELS[key].get('EN', key))
    
    return key


def get_all_labels(language='EN'):
    """
    특정 언어의 모든 라벨 반환
    
    Args:
        language (str): 언어 코드 ('KO', 'EN', 'VN', 'TH')
    
    Returns:
        dict: {key: label} 형태의 딕셔너리
    """
    language = language.upper()
    
    if language not in SUPPORTED_LANGUAGES:
        language = 'EN'
    
    return {
        key: labels.get(language, labels.get('EN', key))
        for key, labels in LANGUAGE_LABELS.items()
    }


def get_supported_languages():
    """지원 언어 목록 반환"""
    return SUPPORTED_LANGUAGES


# 하위 호환성을 위한 별칭
get_input_label = get_label