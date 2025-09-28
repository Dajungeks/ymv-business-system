import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

def show_sales_process_dashboard(load_func):
    """영업 프로세스 대시보드 및 현황 관리"""
    
    st.subheader("📊 영업 프로세스 현황")
    
    try:
        # 영업 프로세스 데이터 로드
        processes = load_func("sales_process")
        
        if not processes:
            st.info("진행 중인 영업 프로세스가 없습니다.")
            st.write("견적서 전환 탭에서 새로운 프로세스를 시작해보세요.")
            return
        
        # 전체 통계
        total_processes = len(processes)
        total_amount = sum(float(p.get('total_amount', 0)) for p in processes)
        
        # 상태별 통계
        status_counts = {}
        for process in processes:
            status = process.get('process_status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # 메트릭 표시
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 프로세스", total_processes)
        with col2:
            st.metric("총 거래액", f"{total_amount:,.0f} VND")
        with col3:
            completed = status_counts.get('completed', 0)
            completion_rate = (completed / total_processes * 100) if total_processes > 0 else 0
            st.metric("완료율", f"{completion_rate:.1f}%")
        with col4:
            in_progress = total_processes - completed
            st.metric("진행 중", in_progress)
        
        # 상태별 분포 차트
        if status_counts:
            st.write("### 📈 상태별 분포")
            
            # 상태명 한글화
            status_korean = {
                'quotation': '견적 단계',
                'approved': '승인됨',
                'ordered': '발주 완료',
                'received': '입고 완료',
                'inspected': '검수 완료',
                'shipped': '출고 완료',
                'completed': '완료'
            }
            
            chart_data = []
            for status, count in status_counts.items():
                chart_data.append({
                    '상태': status_korean.get(status, status),
                    '건수': count
                })
            
            if chart_data:
                chart_df = pd.DataFrame(chart_data)
                st.bar_chart(chart_df.set_index('상태'))
        
        # 프로세스 목록 테이블
        st.write("### 📋 진행 중인 프로세스")
        
        # 테이블용 데이터 준비
        display_data = []
        for process in processes:
            display_data.append({
                '프로세스 번호': process.get('process_number', 'N/A'),
                '고객사': process.get('customer_company', 'N/A'),
                '상품': process.get('item_description', 'N/A')[:30] + '...' if len(process.get('item_description', '')) > 30 else process.get('item_description', 'N/A'),
                '금액 (VND)': f"{float(process.get('total_amount', 0)):,.0f}",
                '상태': status_korean.get(process.get('process_status', ''), process.get('process_status', 'N/A')),
                '생성일': process.get('created_at', 'N/A')[:10] if process.get('created_at') else 'N/A'
            })
        
        if display_data:
            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        # 지연 알림
        render_delay_alerts(processes)
        
    except Exception as e:
        st.error(f"대시보드 로드 중 오류 발생: {str(e)}")

def render_delay_alerts(processes):
    """지연 알림"""
    
    st.write("### ⚠️ 지연 알림")
    
    today = date.today()
    delayed_processes = []
    
    for process in processes:
        expected_date = process.get('expected_delivery_date')
        if expected_date:
            try:
                expected = datetime.strptime(expected_date, '%Y-%m-%d').date()
                if expected < today and process.get('process_status') != 'completed':
                    days_delayed = (today - expected).days
                    delayed_processes.append({
                        'process_number': process.get('process_number', 'N/A'),
                        'customer_company': process.get('customer_company', 'N/A'),
                        'days_delayed': days_delayed,
                        'status': process.get('process_status', 'N/A')
                    })
            except:
                continue
    
    if delayed_processes:
        for delayed in delayed_processes:
            st.warning(
                f"🚨 **{delayed['process_number']}** ({delayed['customer_company']}) - "
                f"{delayed['days_delayed']}일 지연 (상태: {delayed['status']})"
            )
    else:
        st.success("✅ 지연된 프로세스가 없습니다.")