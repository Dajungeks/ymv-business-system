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
        승인 상태 정보 반환 (기존 get_approval_status_info)
        Get approval status information
        """
        status_map = {
            'pending': {'emoji': '⏳', 'icon': '⏳', 'color': 'orange', 'description': '승인 대기'},
            'approved': {'emoji': '✅', 'icon': '✅', 'color': 'green', 'description': '승인됨'},
            'rejected': {'emoji': '❌', 'icon': '❌', 'color': 'red', 'description': '거부됨'}
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
        지출 통계 계산 (기존 calculate_expense_statistics)
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
            status = expense.get('status') or expense.get('approval_status', 'pending')
            normalized_status = StatusHelper.normalize_status(status, 'expense')
            
            if normalized_status == 'approved':
                stats['approved_count'] += 1
                stats['approved_amount'] += amount
            elif normalized_status == 'pending':
                stats['pending_count'] += 1
            elif normalized_status == 'rejected':
                stats['rejected_count'] += 1
            
            # 카테고리별 집계
            category = expense.get('category', '기타')
            stats['category_stats'][category]['count'] += 1
            stats['category_stats'][category]['amount'] += amount
            
            # 월별 집계
            try:
                expense_date = expense.get('expense_date') or expense.get('request_date') or expense.get('created_at', '')
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
        지출 요청서 CSV 다운로드 생성 (기존 create_csv_download)
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
                # 요청자 정보 안전하게 가져오기
                requester_id = expense.get('employee_id') or expense.get('requester')
                employee_info = employee_dict.get(requester_id, {})
                
                csv_data.append({
                    '요청일': expense.get('request_date', ''),
                    '요청자': employee_info.get('name', '알 수 없음'),
                    '직원번호': employee_info.get('employee_id', ''),
                    '부서': expense.get('department', ''),
                    '지출일': expense.get('expense_date', ''),
                    '카테고리': expense.get('category', ''),
                    '금액': expense.get('amount', 0),
                    '내역': expense.get('description') or expense.get('expense_details', ''),
                    '영수증번호': expense.get('receipt_number', ''),
                    '상태': expense.get('status') or expense.get('approval_status', ''),
                    '승인일': expense.get('approved_at', ''),
                    '승인의견': expense.get('approval_comment') or expense.get('approval_comments', '')
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
                    '총액': purchase.get('total_price', 0),
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
    def render_print_form(expense):
        """
        지출 요청서 프린트 폼 렌더링 (기존 render_print_form)
        Render expense request print form
        """
        st.subheader("🖨️ 지출요청서 프린트")
        
        # 프린트 양식 HTML 생성
        print_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h2>지출 요청서</h2>
                <p>EXPENSE REQUEST FORM</p>
            </div>
            
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                <tr>
                    <td style="border: 1px solid black; padding: 10px; background-color: #f0f0f0; width: 150px;">
                        <strong>요청일</strong>
                    </td>
                    <td style="border: 1px solid black; padding: 10px;">{expense.get('request_date', '')}</td>
                    <td style="border: 1px solid black; padding: 10px; background-color: #f0f0f0; width: 150px;">
                        <strong>지출일</strong>
                    </td>
                    <td style="border: 1px solid black; padding: 10px;">{expense.get('expense_date', '')}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid black; padding: 10px; background-color: #f0f0f0;">
                        <strong>부서</strong>
                    </td>
                    <td style="border: 1px solid black; padding: 10px;">{expense.get('department', 'N/A')}</td>
                    <td style="border: 1px solid black; padding: 10px; background-color: #f0f0f0;">
                        <strong>카테고리</strong>
                    </td>
                    <td style="border: 1px solid black; padding: 10px;">{expense.get('category', '')}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid black; padding: 10px; background-color: #f0f0f0;">
                        <strong>금액</strong>
                    </td>
                    <td style="border: 1px solid black; padding: 10px; font-weight: bold;">{expense.get('amount', 0):,}원</td>
                    <td style="border: 1px solid black; padding: 10px; background-color: #f0f0f0;">
                        <strong>영수증 번호</strong>
                    </td>
                    <td style="border: 1px solid black; padding: 10px;">{expense.get('receipt_number', 'N/A')}</td>
                </tr>
            </table>
            
            <div style="margin-bottom: 20px;">
                <h4 style="margin-bottom: 10px;">지출 내역</h4>
                <div style="border: 1px solid black; padding: 15px; min-height: 100px;">
                    {expense.get('description') or expense.get('expense_details', '')}
                </div>
            </div>
            
            <div style="margin-top: 40px;">
                <table style="width: 100%;">
                    <tr>
                        <td style="text-align: center; padding: 20px;">
                            <div style="border-bottom: 1px solid black; width: 150px; margin: 0 auto 5px;">
                            </div>
                            <span>신청자</span>
                        </td>
                        <td style="text-align: center; padding: 20px;">
                            <div style="border-bottom: 1px solid black; width: 150px; margin: 0 auto 5px;">
                            </div>
                            <span>팀장</span>
                        </td>
                        <td style="text-align: center; padding: 20px;">
                            <div style="border-bottom: 1px solid black; width: 150px; margin: 0 auto 5px;">
                            </div>
                            <span>승인자</span>
                        </td>
                    </tr>
                </table>
            </div>
        </div>
        """
        
        # 프린트 옵션 제공
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # HTML 다운로드
            st.download_button(
                label="📄 HTML 다운로드",
                data=f"<html><body>{print_html}</body></html>",
                file_name=f"expense_request_{expense.get('id', 'unknown')}.html",
                mime="text/html"
            )
        
        with col2:
            # 클립보드 복사용 텍스트
            text_content = f"""
지출 요청서

요청일: {expense.get('request_date', '')}
지출일: {expense.get('expense_date', '')}
부서: {expense.get('department', 'N/A')}
카테고리: {expense.get('category', '')}
금액: {expense.get('amount', 0):,}원
영수증 번호: {expense.get('receipt_number', 'N/A')}

지출 내역:
{expense.get('description') or expense.get('expense_details', '')}
            """
            st.download_button(
                label="📝 텍스트 다운로드",
                data=text_content,
                file_name=f"expense_request_{expense.get('id', 'unknown')}.txt",
                mime="text/plain"
            )
        
        with col3:
            # 프린트 버튼 (간단한 JavaScript)
            if st.button("🖨️ 프린트", key=f"print_simple_{expense.get('id', 'unknown')}"):
                st.write("브라우저 프린트: Ctrl+P를 눌러주세요")
        
        # 프린트 미리보기
        st.markdown("### 📋 프린트 미리보기")
        st.markdown(print_html, unsafe_allow_html=True)


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

def render_print_form(expense):
    """하위 호환성 래퍼 함수"""
    return PrintFormGenerator.render_print_form(expense)