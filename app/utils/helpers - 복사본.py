"""
YMV ERP 시스템 헬퍼 유틸리티
Helper utilities for YMV ERP System
"""

import streamlit as st
import pandas as pd
import io
from datetime import datetime
from collections import defaultdict


class StatusHelper:
    """
    상태 정보 관리 클래스
    Status information management class
    """
    
    @staticmethod
    def get_approval_status_info(status):
        """
        승인 상태 정보 반환
        Get approval status information
        """
        status_map = {
            'pending': {'emoji': '⏳', 'icon': '⏳', 'color': 'orange', 'description': '승인 대기'},
            'approved': {'emoji': '✅', 'icon': '✅', 'color': 'green', 'description': '승인됨'},
            'rejected': {'emoji': '❌', 'icon': '❌', 'color': 'red', 'description': '거부됨'},
            '대기중': {'emoji': '⏳', 'icon': '⏳', 'color': 'orange', 'description': '승인 대기'},
            '승인됨': {'emoji': '✅', 'icon': '✅', 'color': 'green', 'description': '승인됨'},
            '거부됨': {'emoji': '❌', 'icon': '❌', 'color': 'red', 'description': '거부됨'}
        }
        return status_map.get(status, {'emoji': '❓', 'icon': '❓', 'color': 'gray', 'description': '알 수 없음'})
    
    @staticmethod
    def get_purchase_status_info(status):
        """구매 요청 상태 정보"""
        status_map = {
            'requested': {'emoji': '📝', 'color': 'blue', 'description': '요청됨'},
            'ordered': {'emoji': '🛒', 'color': 'orange', 'description': '주문됨'},
            'received': {'emoji': '✅', 'color': 'green', 'description': '입고됨'},
            'cancelled': {'emoji': '❌', 'color': 'red', 'description': '취소됨'},
            '대기중': {'emoji': '⏳', 'color': 'orange', 'description': '대기중'}
        }
        return status_map.get(status, {'emoji': '❓', 'color': 'gray', 'description': '알 수 없음'})
    
    @staticmethod
    def normalize_status(status, status_type='expense'):
        """
        상태값 정규화
        Normalize status values
        """
        if status_type == 'expense':
            if status in ['pending', '대기중']:
                return 'pending'
            elif status in ['approved', '승인됨']:
                return 'approved'
            elif status in ['rejected', '거부됨']:
                return 'rejected'
        elif status_type == 'purchase':
            if status == 'requested':
                return 'requested'
            elif status == 'ordered':
                return 'ordered'
            elif status == 'received':
                return 'received'
            elif status == 'cancelled':
                return 'cancelled'
            elif status == '대기중':
                return 'requested'
        
        return status


class StatisticsCalculator:
    """
    통계 계산 클래스
    Statistics calculation class
    """
    
    @staticmethod
    def calculate_expense_statistics(expenses):
        """
        지출 통계 계산
        Calculate expense statistics
        """
        if not expenses:
            return {
                'total_count': 0,
                'total_amount': 0,
                'approved_count': 0,
                'approved_amount': 0,
                'pending_count': 0,
                'rejected_count': 0,
                'category_stats': {},
                'monthly_stats': {}
            }
        
        stats = {
            'total_count': len(expenses),
            'total_amount': 0,
            'approved_count': 0,
            'approved_amount': 0,
            'pending_count': 0,
            'rejected_count': 0,
            'category_stats': defaultdict(lambda: {'count': 0, 'amount': 0}),
            'monthly_stats': defaultdict(lambda: {'count': 0, 'amount': 0})
        }
        
        for expense in expenses:
            amount = float(expense.get('amount', 0))
            stats['total_amount'] += amount
            
            # 상태별 집계
            status = expense.get('status', 'pending')
            normalized_status = StatusHelper.normalize_status(status, 'expense')
            
            if normalized_status == 'approved':
                stats['approved_count'] += 1
                stats['approved_amount'] += amount
            elif normalized_status == 'pending':
                stats['pending_count'] += 1
            elif normalized_status == 'rejected':
                stats['rejected_count'] += 1
            
            # 카테고리별 집계 (expense_type 사용)
            category = expense.get('expense_type', '기타')
            stats['category_stats'][category]['count'] += 1
            stats['category_stats'][category]['amount'] += amount
            
            # 월별 집계
            try:
                expense_date = expense.get('expense_date') or expense.get('created_at', '')
                if expense_date:
                    if isinstance(expense_date, str):
                        if 'T' in expense_date:
                            dt = datetime.fromisoformat(expense_date.replace('Z', '+00:00'))
                        else:
                            dt = datetime.strptime(expense_date, '%Y-%m-%d')
                    else:
                        dt = expense_date
                    
                    month_key = f"{dt.year}-{dt.month:02d}"
                    stats['monthly_stats'][month_key]['count'] += 1
                    stats['monthly_stats'][month_key]['amount'] += amount
            except:
                continue
        
        # defaultdict를 일반 dict로 변환
        stats['category_stats'] = dict(stats['category_stats'])
        stats['monthly_stats'] = dict(stats['monthly_stats'])
        
        return stats
    
    @staticmethod
    def calculate_purchase_statistics(purchases):
        """구매 요청 통계 계산"""
        if not purchases:
            return {
                'total_count': 0,
                'total_amount': {'KRW': 0, 'USD': 0, 'VND': 0},
                'status_stats': {},
                'category_stats': {},
                'currency_stats': {}
            }
        
        stats = {
            'total_count': len(purchases),
            'total_amount': {'KRW': 0, 'USD': 0, 'VND': 0},
            'status_stats': defaultdict(int),
            'category_stats': defaultdict(lambda: {'count': 0, 'amount': 0}),
            'currency_stats': defaultdict(lambda: {'count': 0, 'amount': 0})
        }
        
        for purchase in purchases:
            # 상태별 집계
            status = purchase.get('status', 'requested')
            stats['status_stats'][status] += 1
            
            # 금액 계산
            quantity = purchase.get('quantity', 0)
            unit_price = purchase.get('unit_price', 0)
            total_price = quantity * unit_price
            currency = purchase.get('currency', 'KRW')
            
            stats['total_amount'][currency] += total_price
            
            # 카테고리별 집계
            category = purchase.get('category', '기타')
            stats['category_stats'][category]['count'] += 1
            stats['category_stats'][category]['amount'] += total_price
            
            # 통화별 집계
            stats['currency_stats'][currency]['count'] += 1
            stats['currency_stats'][currency]['amount'] += total_price
        
        # defaultdict를 일반 dict로 변환
        stats['status_stats'] = dict(stats['status_stats'])
        stats['category_stats'] = dict(stats['category_stats'])
        stats['currency_stats'] = dict(stats['currency_stats'])
        
        return stats
    
    @staticmethod
    def calculate_quotation_statistics(quotations):
        """견적서 통계 계산"""
        if not quotations:
            return {
                'total_count': 0,
                'total_amount': 0,
                'monthly_stats': {},
                'customer_stats': {}
            }
        
        stats = {
            'total_count': len(quotations),
            'total_amount': 0,
            'monthly_stats': defaultdict(lambda: {'count': 0, 'amount': 0}),
            'customer_stats': defaultdict(lambda: {'count': 0, 'amount': 0})
        }
        
        for quotation in quotations:
            amount = float(quotation.get('total_amount', 0))
            stats['total_amount'] += amount
            
            # 고객별 집계
            customer_id = quotation.get('customer_id')
            if customer_id:
                stats['customer_stats'][customer_id]['count'] += 1
                stats['customer_stats'][customer_id]['amount'] += amount
            
            # 월별 집계
            try:
                quote_date = quotation.get('quote_date') or quotation.get('created_at', '')
                if quote_date:
                    if isinstance(quote_date, str):
                        if 'T' in quote_date:
                            dt = datetime.fromisoformat(quote_date.replace('Z', '+00:00'))
                        else:
                            dt = datetime.strptime(quote_date, '%Y-%m-%d')
                    else:
                        dt = quote_date
                    
                    month_key = f"{dt.year}-{dt.month:02d}"
                    stats['monthly_stats'][month_key]['count'] += 1
                    stats['monthly_stats'][month_key]['amount'] += amount
            except:
                continue
        
        # defaultdict를 일반 dict로 변환
        stats['monthly_stats'] = dict(stats['monthly_stats'])
        stats['customer_stats'] = dict(stats['customer_stats'])
        
        return stats


class CSVGenerator:
    """
    CSV 생성 클래스
    CSV generation class
    """
    
    @staticmethod
    def create_csv_download(expenses, employees):
        """
        지출 요청서 CSV 다운로드 생성
        Create CSV download for expense reports
        """
        try:
            if not expenses:
                return ""
            
            # 직원 정보를 딕셔너리로 변환
            employee_dict = {}
            if employees:
                for emp in employees:
                    emp_id = emp.get('id')
                    if emp_id:
                        employee_dict[emp_id] = emp
            
            # CSV 데이터 준비
            csv_data = []
            for expense in expenses:
                # 요청자 정보 (requester 필드 사용)
                requester_id = expense.get('requester')
                employee_info = employee_dict.get(requester_id, {})
                
                # 요청일 (created_at에서 날짜만 추출)
                request_date = ''
                if expense.get('created_at'):
                    try:
                        dt = datetime.fromisoformat(str(expense['created_at']).replace('Z', '+00:00'))
                        request_date = dt.strftime('%Y-%m-%d')
                    except:
                        request_date = str(expense['created_at'])[:10]
                
                csv_data.append({
                    '요청일': request_date,
                    '요청자': employee_info.get('name', '알 수 없음'),
                    '직원번호': employee_info.get('employee_id', ''),
                    '부서': expense.get('department', ''),
                    '지출일': expense.get('expense_date', ''),
                    '카테고리': expense.get('expense_type', ''),
                    '금액': expense.get('amount', 0),
                    '통화': expense.get('currency', 'VND'),
                    '내역': expense.get('description', ''),
                    '목적': expense.get('business_purpose', ''),
                    '공급업체': expense.get('vendor', ''),
                    '영수증번호': expense.get('receipt_number', ''),
                    '상태': expense.get('status', ''),
                    '승인일': expense.get('approved_at', ''),
                    '승인의견': expense.get('approval_comment', '')
                })
            
            # DataFrame으로 변환하고 CSV 생성
            df = pd.DataFrame(csv_data)
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
            return csv_buffer.getvalue().encode('utf-8-sig')
            
        except Exception as e:
            st.error(f"CSV 생성 오류: {str(e)}")
            return None
    
    @staticmethod
    def create_purchase_csv(purchases, employees):
        """구매 요청 CSV 생성"""
        try:
            if not purchases:
                return ""
            
            # 직원 정보를 딕셔너리로 변환
            employee_dict = {}
            if employees:
                for emp in employees:
                    emp_id = emp.get('id')
                    if emp_id:
                        employee_dict[emp_id] = emp
            
            # CSV 데이터 준비
            csv_data = []
            for purchase in purchases:
                requester_id = purchase.get('requester')
                employee_info = employee_dict.get(requester_id, {})
                
                csv_data.append({
                    '요청일': purchase.get('request_date', ''),
                    '요청자': employee_info.get('name', '알 수 없음'),
                    '카테고리': purchase.get('category', ''),
                    '품목명': purchase.get('item_name', ''),
                    '수량': purchase.get('quantity', 0),
                    '단위': purchase.get('unit', '개'),
                    '단가': purchase.get('unit_price', 0),
                    '이액': purchase.get('total_price', 0),
                    '통화': purchase.get('currency', 'KRW'),
                    '공급업체': purchase.get('supplier', ''),
                    '긴급도': purchase.get('urgency', '보통'),
                    '상태': purchase.get('status', ''),
                    '비고': purchase.get('notes', '')
                })
            
            # DataFrame으로 변환하고 CSV 생성
            df = pd.DataFrame(csv_data)
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
            return csv_buffer.getvalue().encode('utf-8-sig')
            
        except Exception as e:
            st.error(f"구매 요청 CSV 생성 오류: {str(e)}")
            return None


class PrintFormGenerator:
    """
    프린트 폼 생성 클래스
    Print form generation class
    """
    
    @staticmethod
    def render_print_form(expense, employees):
        """
        지출 요청서 프린트 폼 렌더링 (템플릿 분리 버전)
        Render expense request print form (template separated version)
        """
        import os
        
        st.subheader("🖨️ 지출요청서 프린트")
        
        # 직원 정보를 딕셔너리로 변환
        employee_dict = {}
        if employees:
            for emp in employees:
                emp_id = emp.get('id')
                if emp_id:
                    employee_dict[emp_id] = emp
        
        # 요청자 정보
        requester_id = expense.get('requester')
        requester_info = employee_dict.get(requester_id, {})
        requester_name = requester_info.get('name', '알 수 없음')
        requester_emp_id = requester_info.get('employee_id', 'N/A')
        
        # 승인자 정보
        approver_name = 'N/A'
        approver_date = ''
        if expense.get('approved_by'):
            approver_info = employee_dict.get(expense['approved_by'], {})
            approver_name = approver_info.get('name', '알 수 없음')
        
        if expense.get('approved_at'):
            try:
                dt = datetime.fromisoformat(str(expense['approved_at']).replace('Z', '+00:00'))
                approver_date = dt.strftime('%Y-%m-%d')
            except:
                approver_date = str(expense['approved_at'])[:10]
        
        # 요청일 추출
        request_date = 'N/A'
        if expense.get('created_at'):
            try:
                dt = datetime.fromisoformat(str(expense['created_at']).replace('Z', '+00:00'))
                request_date = dt.strftime('%Y-%m-%d')
            except:
                request_date = str(expense['created_at'])[:10]
        
        # 통화
        currency = expense.get('currency', 'VND')
        
        # 상태 정보
        status = expense.get('status', 'pending')
        status_info = StatusHelper.get_approval_status_info(status)
        status_emoji = status_info.get('emoji', '❓')
        status_description = status_info.get('description', '알 수 없음')
        status_color = status_info.get('color', 'gray')
        
        # 상태별 배경색
        status_bg_colors = {
            'orange': '#fff3cd',
            'green': '#d1e7dd',
            'red': '#f8d7da',
            'gray': '#e9ecef'
        }
        status_bg = status_bg_colors.get(status_color, '#e9ecef')
        
        # 반려 사유 HTML
        rejection_reason = ''
        if status == 'rejected' and expense.get('approval_comment'):
            rejection_reason = f"""
                <div class="rejection-reason">
                    <h3>❌ 반려 사유 (Rejection Reason)</h3>
                    <div class="content">{expense.get('approval_comment')}</div>
                </div>
            """
        
        # 결재란 서명 및 날짜
        requester_signature = f'<div style="margin-top: 20px; font-weight: bold;">{requester_name}</div>'
        
        approver_signature = ''
        approver_signature_class = ''
        approver_date_text = '날짜 (Date):'
        approver_date_class = ''
        
        if status in ['approved', 'rejected']:
            approver_signature = f'<div style="margin-top: 20px; font-weight: bold;">{approver_name}</div>'
            approver_date_text = f'날짜 (Date): {approver_date}'
            if status == 'approved':
                approver_signature_class = 'approved-signature'
                approver_date_class = 'approved-signature'
        
        # 템플릿 파일 읽기
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'expense_print_template.html')
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
        except FileNotFoundError:
            st.error("❌ 프린트 템플릿 파일을 찾을 수 없습니다. templates/expense_print_template.html 파일이 있는지 확인하세요.")
            return
        
        # 템플릿 변수 치환
        print_html = template.format(
            expense_id=expense.get('id', 'N/A'),
            status_bg=status_bg,
            status_color=status_color,
            status_emoji=status_emoji,
            status_description=status_description,
            requester_name=requester_name,
            requester_emp_id=requester_emp_id,
            request_date=request_date,
            department=expense.get('department', 'N/A'),
            expense_date=expense.get('expense_date', 'N/A'),
            expense_type=expense.get('expense_type', 'N/A'),
            amount=f"{expense.get('amount', 0):,}",
            currency=currency,
            payment_method=expense.get('payment_method', 'N/A'),
            urgency=expense.get('urgency', '보통'),
            vendor=expense.get('vendor', 'N/A'),
            receipt_number=expense.get('receipt_number', 'N/A'),
            description=expense.get('description', '내용 없음'),
            business_purpose=expense.get('business_purpose') or expense.get('purpose', '내용 없음'),
            rejection_reason=rejection_reason,
            requester_signature=requester_signature,
            approver_signature=approver_signature,
            approver_signature_class=approver_signature_class,
            approver_date_text=approver_date_text,
            approver_date_class=approver_date_class,
            generated_time=datetime.now().strftime('%Y-%m-%d %H:%M')
        )
        
        # 다운로드 옵션
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                label="📄 HTML 다운로드",
                data=print_html,
                file_name=f"expense_request_{expense.get('id', 'unknown')}.html",
                mime="text/html",
                help="HTML 파일로 저장하여 브라우저에서 열어 프린트할 수 있습니다."
            )
        with col2:
                    # 반려 사유 텍스트 (조건부)
                    rejection_text = ''
                    if status == 'rejected' and expense.get('approval_comment'):
                        rejection_text = f"[반려 사유]\n{expense.get('approval_comment', '')}\n\n"
                    
                    # CEO 이름 (조건부)
                    ceo_name_text = ''
                    ceo_date_text = ''
                    if status in ['approved', 'rejected']:
                        ceo_name_text = approver_name
                        ceo_date_text = approver_date
                    
                    text_content = f"""
        ═══════════════════════════════════════════════════════
                    CÔNG TY TNHH YUMOLD VIỆT NAM
                지출 요청서 (EXPENSE REQUEST FORM)
        ═══════════════════════════════════════════════════════

        [문서 상태] {status_emoji} {status_description}

        [기본 정보]
        요청자: {requester_name} ({requester_emp_id})
        요청일: {request_date}
        부서: {expense.get('department', 'N/A')}
        지출일: {expense.get('expense_date', 'N/A')}
        지출 유형: {expense.get('expense_type', 'N/A')}
        금액: {expense.get('amount', 0):,} {currency}
        결제 방법: {expense.get('payment_method', 'N/A')}
        긴급도: {expense.get('urgency', '보통')}
        공급업체: {expense.get('vendor', 'N/A')}
        영수증 번호: {expense.get('receipt_number', 'N/A')}

        [지출 내역]
        {expense.get('description', '내용 없음')}

        [사업 목적]
        {expense.get('business_purpose') or expense.get('purpose', '내용 없음')}

        {rejection_text}───────────────────────────────────────────────────────
        결재란
        신청자: {requester_name}       팀장:              CEO: {ceo_name_text}

        날짜: {request_date}                              날짜: {ceo_date_text}

        ═══════════════════════════════════════════════════════
        Document ID: EXP-{expense.get('id', 'N/A')}
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    """
                    st.download_button(
                        label="📝 텍스트 다운로드",
                        data=text_content,
                        file_name=f"expense_request_{expense.get('id', 'unknown')}.txt",
                        mime="text/plain",
                        help="텍스트 형식으로 저장합니다."
                    )
        with col3:
            st.info("💡 HTML을 다운로드하여\n브라우저에서 열고\n프린트하세요!")
        
        # 프린트 미리보기
        st.markdown("---")
        st.markdown("### 📋 프린트 미리보기")
        st.components.v1.html(print_html, height=1400, scrolling=True)

# 하위 호환성을 위한 래퍼 함수들
def get_approval_status_info(status):
    """하위 호환성 래퍼 함수"""
    return StatusHelper.get_approval_status_info(status)

def calculate_expense_statistics(expenses):
    """하위 호환성 래퍼 함수"""
    return StatisticsCalculator.calculate_expense_statistics(expenses)

def create_csv_download(expenses, employees):
    """하위 호환성 래퍼 함수"""
    return CSVGenerator.create_csv_download(expenses, employees)

def render_print_form(expense, employees):
    """하위 호환성 래퍼 함수"""
    return PrintFormGenerator.render_print_form(expense, employees)