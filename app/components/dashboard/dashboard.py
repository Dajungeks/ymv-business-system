"""
YMV ERP 시스템 - 대시보드 컴포넌트 (Step 9 완료)
Dashboard Component for YMV ERP System - Step 9 Complete
백업 파일과 호환되는 안전한 필드 접근 방식 적용
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from collections import defaultdict
import calendar


def show_dashboard_main(load_data_func, get_current_user_func):
    """
    메인 대시보드 함수 (백업 파일과 호환)
    Main dashboard function compatible with backup file
    """
    st.title("📊 YMV 관리 시스템 대시보드")
    
    # 현재 사용자 정보
    current_user = get_current_user_func()
    if current_user:
        st.write(f"👋 환영합니다, **{current_user.get('name', 'Unknown')}**님!")
        
        # 사용자 권한에 따른 환영 메시지
        role = current_user.get('role', 'employee')
        if role == 'manager':
            st.info("🔑 관리자 권한으로 로그인되었습니다. 모든 기능을 사용할 수 있습니다.")
        else:
            st.info("👤 일반 사용자로 로그인되었습니다.")
    
    # 3개 컬럼으로 메트릭 표시
    col1, col2, col3 = st.columns(3)
    
    # 개요 통계 렌더링
    render_overview_metrics(col1, col2, col3, load_data_func)
    
    st.divider()
    
    # 2개 컬럼으로 차트와 최근 활동 표시
    chart_col, activity_col = st.columns([2, 1])
    
    with chart_col:
        render_status_charts(load_data_func)
    
    with activity_col:
        render_recent_activities(load_data_func, current_user)


def render_overview_metrics(col1, col2, col3, load_data_func):
    """
    개요 통계 메트릭 렌더링 (안전한 필드 체크)
    Render overview metrics with safe field checking
    """
    try:
        # 지출 요청서 통계
        with col1:
            expenses = load_data_func("expenses", "*", None)
            if expenses:
                total_expenses = len(expenses)
                # 안전한 필드 접근 - 백업 파일과 호환
                pending_count = sum(1 for exp in expenses if exp.get('approval_status') == '대기중' or exp.get('status') == 'pending')
                approved_count = sum(1 for exp in expenses if exp.get('approval_status') == '승인됨' or exp.get('status') == 'approved')
                
                st.metric(
                    label="💳 지출 요청서",
                    value=f"{total_expenses}건",
                    delta=f"대기: {pending_count}건"
                )
                
                # 승인률 계산
                if total_expenses > 0:
                    approval_rate = (approved_count / total_expenses) * 100
                    st.caption(f"승인률: {approval_rate:.1f}%")
            else:
                st.metric(label="💳 지출 요청서", value="0건")
        
        # 견적서 통계
        with col2:
            quotations = load_data_func("quotations", "*", None)
            if quotations:
                total_quotations = len(quotations)
                # 안전한 필드 접근
                total_amount = sum(
                    float(q.get('total_amount', 0)) for q in quotations 
                    if q.get('total_amount') is not None
                )
                
                st.metric(
                    label="📋 견적서",
                    value=f"{total_quotations}건",
                    delta=f"총액: {total_amount:,.0f}원"
                )
            else:
                st.metric(label="📋 견적서", value="0건")
        
        # 구매 요청 통계
        with col3:
            purchases = load_data_func("purchases", "*", None)
            if purchases:
                total_purchases = len(purchases)
                pending_purchases = sum(1 for p in purchases if p.get('status') == '대기중' or p.get('status') == 'requested')
                
                st.metric(
                    label="🛒 구매 요청",
                    value=f"{total_purchases}건",
                    delta=f"대기: {pending_purchases}건"
                )
            else:
                st.metric(label="🛒 구매 요청", value="0건")
                
    except Exception as e:
        st.error(f"통계 데이터 로드 중 오류: {str(e)}")


def render_status_charts(load_data_func):
    """
    상태별 차트 렌더링
    Render status charts for different modules
    """
    st.subheader("📈 상태별 현황")
    
    # 탭으로 차트 구분
    chart_tab1, chart_tab2, chart_tab3 = st.tabs(["지출 요청서", "구매 요청", "월별 동향"])
    
    with chart_tab1:
        render_expense_status_chart(load_data_func)
    
    with chart_tab2:
        render_purchase_status_chart(load_data_func)
    
    with chart_tab3:
        render_monthly_trends(load_data_func)


def render_expense_status_chart(load_data_func):
    """지출 요청서 상태별 차트 (백업 파일과 호환)"""
    try:
        expenses = load_data_func("expenses", "*", None)
        if expenses:
            # 상태별 집계 - 백업 파일과 호환되는 방식
            status_count = defaultdict(int)
            for exp in expenses:
                # 두 가지 필드명 모두 지원
                status = exp.get('approval_status') or exp.get('status', '미분류')
                # 상태값 정규화
                if status in ['pending', '대기중']:
                    status = '대기중'
                elif status in ['approved', '승인됨']:
                    status = '승인됨'
                elif status in ['rejected', '거부됨']:
                    status = '거부됨'
                
                status_count[status] += 1
            
            if status_count:
                # DataFrame으로 변환
                df = pd.DataFrame(
                    list(status_count.items()),
                    columns=['상태', '건수']
                )
                
                # 바 차트 표시
                st.bar_chart(df.set_index('상태'))
                
                # 상세 정보 표시
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**상태별 상세:**")
                    for status, count in status_count.items():
                        st.write(f"• {status}: {count}건")
                
                with col2:
                    # 승인률 계산
                    total = sum(status_count.values())
                    approved = status_count.get('승인됨', 0)
                    if total > 0:
                        rate = (approved / total) * 100
                        st.metric("승인률", f"{rate:.1f}%")
        else:
            st.info("지출 요청서 데이터가 없습니다.")
            
    except Exception as e:
        st.error(f"지출 요청서 차트 오류: {str(e)}")


def render_purchase_status_chart(load_data_func):
    """구매 요청 상태별 차트"""
    try:
        purchases = load_data_func("purchases", "*", None)
        if purchases:
            # 상태별 집계
            status_count = defaultdict(int)
            for purchase in purchases:
                status = purchase.get('status', '미분류')
                # 상태값 정규화
                if status == 'requested':
                    status = '요청됨'
                elif status == 'ordered':
                    status = '주문됨'
                elif status == 'received':
                    status = '입고됨'
                elif status == 'cancelled':
                    status = '취소됨'
                elif status == '대기중':
                    status = '대기중'
                
                status_count[status] += 1
            
            if status_count:
                # DataFrame으로 변환
                df = pd.DataFrame(
                    list(status_count.items()),
                    columns=['상태', '건수']
                )
                
                # 상태 분포 표시
                st.write("**구매 요청 상태 분포:**")
                for status, count in status_count.items():
                    percentage = (count / sum(status_count.values())) * 100
                    st.write(f"• {status}: {count}건 ({percentage:.1f}%)")
                
                # 바 차트 표시
                st.bar_chart(df.set_index('상태'))
        else:
            st.info("구매 요청 데이터가 없습니다.")
            
    except Exception as e:
        st.error(f"구매 요청 차트 오류: {str(e)}")


def render_monthly_trends(load_data_func):
    """월별 동향 차트 (백업 파일과 호환)"""
    try:
        # 현재 년도 기준으로 월별 데이터 수집
        current_year = datetime.now().year
        monthly_data = defaultdict(lambda: {'expenses': 0, 'purchases': 0, 'quotations': 0})
        
        # 지출 요청서 월별 집계
        expenses = load_data_func("expenses", "*", None)
        if expenses:
            for exp in expenses:
                # 여러 날짜 필드 지원
                created_at = exp.get('created_at') or exp.get('request_date') or exp.get('expense_date')
                if created_at:
                    try:
                        # 다양한 날짜 형식 지원
                        if isinstance(created_at, str):
                            if 'T' in created_at:
                                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            else:
                                dt = datetime.strptime(created_at, '%Y-%m-%d')
                        else:
                            dt = created_at
                        
                        if dt.year == current_year:
                            month_name = calendar.month_name[dt.month]
                            monthly_data[month_name]['expenses'] += 1
                    except:
                        continue
        
        # 구매 요청 월별 집계
        purchases = load_data_func("purchases", "*", None)
        if purchases:
            for purchase in purchases:
                created_at = purchase.get('created_at') or purchase.get('request_date')
                if created_at:
                    try:
                        if isinstance(created_at, str):
                            if 'T' in created_at:
                                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            else:
                                dt = datetime.strptime(created_at, '%Y-%m-%d')
                        else:
                            dt = created_at
                        
                        if dt.year == current_year:
                            month_name = calendar.month_name[dt.month]
                            monthly_data[month_name]['purchases'] += 1
                    except:
                        continue
        
        # 견적서 월별 집계
        quotations = load_data_func("quotations", "*", None)
        if quotations:
            for quot in quotations:
                created_at = quot.get('created_at') or quot.get('quote_date')
                if created_at:
                    try:
                        if isinstance(created_at, str):
                            if 'T' in created_at:
                                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            else:
                                dt = datetime.strptime(created_at, '%Y-%m-%d')
                        else:
                            dt = created_at
                        
                        if dt.year == current_year:
                            month_name = calendar.month_name[dt.month]
                            monthly_data[month_name]['quotations'] += 1
                    except:
                        continue
        
        # 차트 데이터 준비
        if monthly_data:
            months = []
            expenses_counts = []
            purchases_counts = []
            quotations_counts = []
            
            # 현재 월까지만 표시
            current_month = datetime.now().month
            for i in range(1, current_month + 1):
                month_name = calendar.month_name[i]
                months.append(month_name[:3])  # 축약형
                expenses_counts.append(monthly_data[month_name]['expenses'])
                purchases_counts.append(monthly_data[month_name]['purchases'])
                quotations_counts.append(monthly_data[month_name]['quotations'])
            
            # DataFrame 생성
            df = pd.DataFrame({
                '월': months,
                '지출요청서': expenses_counts,
                '구매요청': purchases_counts,
                '견적서': quotations_counts
            })
            
            st.write(f"**{current_year}년 월별 등록 현황:**")
            st.line_chart(df.set_index('월'))
            
            # 요약 통계
            total_expenses = sum(expenses_counts)
            total_purchases = sum(purchases_counts)
            total_quotations = sum(quotations_counts)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("연간 지출요청서", f"{total_expenses}건")
            with col2:
                st.metric("연간 구매요청", f"{total_purchases}건")
            with col3:
                st.metric("연간 견적서", f"{total_quotations}건")
        else:
            st.info("월별 동향 데이터가 없습니다.")
            
    except Exception as e:
        st.error(f"월별 동향 차트 오류: {str(e)}")


def render_recent_activities(load_data_func, current_user):
    """
    최근 활동 렌더링 (백업 파일과 호환)
    Render recent activities compatible with backup file
    """
    st.subheader("🕒 최근 활동")
    
    try:
        recent_activities = []
        
        # 현재 사용자의 최근 지출 요청서 (최대 5개)
        expenses = load_data_func("expenses", "*", None)
        if expenses and current_user:
            user_expenses = []
            
            # 요청자 필드 확인 (여러 필드명 지원)
            for exp in expenses:
                requester_match = False
                
                # employee_id 필드가 있는 경우
                if exp.get('employee_id') == current_user.get('id'):
                    requester_match = True
                # requester 필드가 있는 경우
                elif exp.get('requester') == current_user.get('id'):
                    requester_match = True
                # user_id 필드가 있는 경우
                elif exp.get('user_id') == current_user.get('id'):
                    requester_match = True
                
                if requester_match:
                    user_expenses.append(exp)
            
            # 최신순 정렬
            user_expenses.sort(key=lambda x: x.get('created_at') or x.get('request_date', ''), reverse=True)
            
            for exp in user_expenses[:3]:  # 최근 3개만
                # 날짜 처리
                created_date = exp.get('created_at') or exp.get('request_date') or exp.get('expense_date', '')
                if created_date:
                    try:
                        if isinstance(created_date, str):
                            if 'T' in created_date:
                                dt = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                            else:
                                dt = datetime.strptime(created_date, '%Y-%m-%d')
                            date_str = dt.strftime('%m/%d')
                        else:
                            date_str = created_date.strftime('%m/%d')
                    except:
                        date_str = '날짜불명'
                else:
                    date_str = '날짜불명'
                
                amount = exp.get('amount', 0)
                # 상태 필드 통합
                status = exp.get('approval_status') or exp.get('status', '미분류')
                if status == 'pending':
                    status = '대기중'
                elif status == 'approved':
                    status = '승인됨'
                elif status == 'rejected':
                    status = '거부됨'
                
                # 내용 필드 통합
                content = exp.get('expense_details') or exp.get('description') or exp.get('content', '내용없음')
                
                recent_activities.append({
                    'date': date_str,
                    'type': '지출요청서',
                    'content': content[:20] + ('...' if len(content) > 20 else ''),
                    'amount': f"{amount:,}원",
                    'status': status
                })
        
        # 최근 구매 요청 (관리자인 경우 전체, 일반사용자인 경우 본인것만)
        purchases = load_data_func("purchases", "*", None)
        if purchases and current_user:
            if current_user.get('role') == 'manager':
                user_purchases = purchases  # 관리자는 전체
            else:
                user_purchases = [
                    p for p in purchases 
                    if p.get('requester') == current_user.get('id')
                ]
            
            user_purchases.sort(key=lambda x: x.get('created_at') or x.get('request_date', ''), reverse=True)
            
            for purchase in user_purchases[:2]:  # 최근 2개만
                # 날짜 처리
                created_date = purchase.get('created_at') or purchase.get('request_date', '')
                if created_date:
                    try:
                        if isinstance(created_date, str):
                            if 'T' in created_date:
                                dt = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                            else:
                                dt = datetime.strptime(created_date, '%Y-%m-%d')
                            date_str = dt.strftime('%m/%d')
                        else:
                            date_str = created_date.strftime('%m/%d')
                    except:
                        date_str = '날짜불명'
                else:
                    date_str = '날짜불명'
                
                item_name = purchase.get('item_name', '품목불명')
                status = purchase.get('status', '미분류')
                quantity = purchase.get('quantity', 0)
                unit_price = purchase.get('unit_price', 0)
                currency = purchase.get('currency', 'KRW')
                
                # 상태 정규화
                if status == 'requested':
                    status = '요청됨'
                elif status == 'ordered':
                    status = '주문됨'
                elif status == 'received':
                    status = '입고됨'
                elif status == 'cancelled':
                    status = '취소됨'
                
                recent_activities.append({
                    'date': date_str,
                    'type': '구매요청',
                    'content': f"{item_name} {quantity}개",
                    'amount': f"{unit_price:,}{currency}",
                    'status': status
                })
        
        # 활동 내역 표시
        if recent_activities:
            for activity in recent_activities:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**{activity['date']}** - {activity['type']}")
                        st.caption(activity['content'])
                    
                    with col2:
                        st.write(activity['amount'])
                        
                        # 상태에 따른 색상 표시
                        if activity['status'] in ['승인됨', '입고됨']:
                            st.success(activity['status'])
                        elif activity['status'] in ['거부됨', '취소됨']:
                            st.error(activity['status'])
                        else:
                            st.warning(activity['status'])
                    
                    st.divider()
        else:
            st.info("최근 활동이 없습니다.")
            
    except Exception as e:
        st.error(f"최근 활동 로드 중 오류: {str(e)}")


def get_dashboard_metrics_summary(load_data_func):
    """
    대시보드 메트릭 요약 (다른 컴포넌트에서 재사용 가능)
    Get dashboard metrics summary for reuse in other components
    """
    try:
        summary = {
            'expenses': {'total': 0, 'pending': 0, 'approved': 0},
            'purchases': {'total': 0, 'pending': 0, 'completed': 0},
            'quotations': {'total': 0, 'total_amount': 0}
        }
        
        # 지출 요청서 통계
        expenses = load_data_func("expenses", "*", None)
        if expenses:
            summary['expenses']['total'] = len(expenses)
            summary['expenses']['pending'] = sum(1 for exp in expenses if exp.get('approval_status') == '대기중' or exp.get('status') == 'pending')
            summary['expenses']['approved'] = sum(1 for exp in expenses if exp.get('approval_status') == '승인됨' or exp.get('status') == 'approved')
        
        # 구매 요청 통계
        purchases = load_data_func("purchases", "*", None)
        if purchases:
            summary['purchases']['total'] = len(purchases)
            summary['purchases']['pending'] = sum(1 for p in purchases if p.get('status') in ['대기중', 'requested'])
            summary['purchases']['completed'] = sum(1 for p in purchases if p.get('status') in ['완료됨', 'received'])
        
        # 견적서 통계
        quotations = load_data_func("quotations", "*", None)
        if quotations:
            summary['quotations']['total'] = len(quotations)
            summary['quotations']['total_amount'] = sum(
                float(q.get('total_amount', 0)) for q in quotations 
                if q.get('total_amount') is not None
            )
        
        return summary
        
    except Exception as e:
        st.error(f"대시보드 요약 통계 오류: {str(e)}")
        return None