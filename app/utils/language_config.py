"""
Language Configuration for Hot Runner Order Sheet
영어(EN)와 베트남어(VN) 라벨 매핑
"""

# 언어별 라벨 매핑
LANGUAGE_LABELS = {
    # Customer Section
    'customer': {'EN': 'Customer', 'VN': 'Khách hàng'},
    'delivery_to': {'EN': 'Delivery To', 'VN': 'Giao đến'},
    'project_name': {'EN': 'Project Name', 'VN': 'Tên dự án'},
    'part_name': {'EN': 'Part Name', 'VN': 'Tên chi tiết'},
    'mold_no': {'EN': 'Mold No.', 'VN': 'Số khuôn'},
    'ymv_no': {'EN': 'YMV No.', 'VN': 'Số YMV'},
    'sales_contact': {'EN': 'Sales Contact', 'VN': 'Người liên hệ'},
    'injection_ton': {'EN': 'Injection Ton', 'VN': 'Tấn ép'},
    'resin': {'EN': 'Resin', 'VN': 'Nhựa'},
    'additive': {'EN': 'Additive', 'VN': 'Phụ gia'},
    'color_change': {'EN': 'Color Change', 'VN': 'Đổi màu'},
    'order_type': {'EN': 'Order Type', 'VN': 'Loại đơn hàng'},
    
    # Base Section
    'base': {'EN': 'BASE', 'VN': 'ĐẾ'},
    'plate': {'EN': 'PLATE', 'VN': 'TẤM'},
    'top': {'EN': 'TOP', 'VN': 'TRÊN'},
    'space': {'EN': 'SPACE', 'VN': 'KHOẢNG'},
    'holding': {'EN': 'HOLDING', 'VN': 'GIỮ'},
    'width': {'EN': 'W', 'VN': 'R'},
    'length': {'EN': 'L', 'VN': 'D'},
    'height': {'EN': 'H', 'VN': 'C'},
    'base_processor': {'EN': 'BASE Processor', 'VN': 'Nhà sản xuất đế'},
    'cooling_pt_tap': {'EN': 'Cooling PT/TAP', 'VN': 'Làm mát PT/TAP'},
    
    # Nozzle Section
    'nozzle': {'EN': 'NOZZLE', 'VN': 'VÒI PHUN'},
    'nozzle_type': {'EN': 'Type', 'VN': 'Loại'},
    'gate_close': {'EN': 'Gate Close', 'VN': 'Đóng cổng'},
    'qty': {'EN': 'QTY', 'VN': 'SL'},
    'ht_type': {'EN': 'H/T Type', 'VN': 'Loại H/T'},
    'nozzle_length': {'EN': 'Length', 'VN': 'Chiều dài'},
    
    # Manifold Section
    'manifold': {'EN': 'MANIFOLD', 'VN': 'ỐNG DẪN'},
    'manifold_type': {'EN': 'Type', 'VN': 'Loại'},
    'manifold_standard': {'EN': 'Standard', 'VN': 'Tiêu chuẩn'},
    'manifold_ht_type': {'EN': 'H/T Type', 'VN': 'Loại H/T'},
    
    # Cylinder Section
    'cylinder': {'EN': 'CYLINDER', 'VN': 'XI LANH'},
    'cylinder_type': {'EN': 'Type', 'VN': 'Loại'},
    
    # Sensor Section
    'sensor': {'EN': 'SENSOR', 'VN': 'CẢM BIẾN'},
    'sensor_type': {'EN': 'Type', 'VN': 'Loại'},
    
    # Timer Connector
    'timer_connector': {'EN': 'TIMER CONNECTOR', 'VN': 'ĐẦU NỐI BỘ ĐẾM'},
    'sol_volt': {'EN': 'SOL VOLT', 'VN': 'ĐIỆN ÁP SOL'},
    'sol_control': {'EN': 'SOL Control', 'VN': 'Điều khiển SOL'},
    'pin_type': {'EN': 'PIN Type', 'VN': 'Loại PIN'},
    'con_type': {'EN': 'CON Type', 'VN': 'Loại CON'},
    'buried': {'EN': 'BURIED', 'VN': 'CHÔN'},
    'location': {'EN': 'Location', 'VN': 'Vị trí'},
    
    # Heater Connector
    'heater_connector': {'EN': 'HEATER CONNECTOR', 'VN': 'ĐẦU NỐI NHIỆT'},
    
    # ID Card
    'id_card': {'EN': 'ID CARD', 'VN': 'THẺ ID'},
    'id_card_type': {'EN': 'Type', 'VN': 'Loại'},
    
    # NL
    'nl': {'EN': 'NL', 'VN': 'NL'},
    'nl_phi': {'EN': 'Φ', 'VN': 'Φ'},
    'nl_sr': {'EN': 'S.R', 'VN': 'S.R'},
    'locate_ring': {'EN': 'LOCATE RING', 'VN': 'VÒNG ĐỊNH VỊ'},
    
    # Gate Section
    'gate': {'EN': 'GATE', 'VN': 'CỔNG'},
    'gate_phi': {'EN': 'GATE Φ', 'VN': 'CỔNG Φ'},
    'gate_length': {'EN': 'Length', 'VN': 'Chiều dài'},
    
    # Additional
    'spare_list': {'EN': 'SPARE LIST', 'VN': 'DANH SÁCH PHỤ TÙNG'},
    'special_notes': {'EN': 'Special Notes', 'VN': 'Ghi chú đặc biệt'},
    
    # Actions
    'save': {'EN': 'Save', 'VN': 'Lưu'},
    'cancel': {'EN': 'Cancel', 'VN': 'Hủy'},
    'print': {'EN': 'Print', 'VN': 'In'},
    'download': {'EN': 'Download', 'VN': 'Tải xuống'},
    'search': {'EN': 'Search', 'VN': 'Tìm kiếm'},
    'edit': {'EN': 'Edit', 'VN': 'Sửa'},
    'delete': {'EN': 'Delete', 'VN': 'Xóa'},
    
    # Status
    'draft': {'EN': 'Draft', 'VN': 'Bản nháp'},
    'approved': {'EN': 'Approved', 'VN': 'Đã duyệt'},
    'completed': {'EN': 'Completed', 'VN': 'Hoàn thành'},
}

def get_input_label(key, language='EN'):
    """
    언어별 라벨 반환
    
    Args:
        key (str): 라벨 키
        language (str): 언어 코드 ('EN' 또는 'VN')
    
    Returns:
        str: 해당 언어의 라벨 (없으면 키 그대로 반환)
    """
    if key in LANGUAGE_LABELS:
        return LANGUAGE_LABELS[key].get(language, key)
    return key

def get_all_labels(language='EN'):
    """
    특정 언어의 모든 라벨 반환
    
    Args:
        language (str): 언어 코드
    
    Returns:
        dict: {key: label} 형태의 딕셔너리
    """
    return {key: labels.get(language, key) for key, labels in LANGUAGE_LABELS.items()}
