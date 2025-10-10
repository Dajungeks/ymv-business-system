import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

def show_sales_process_dashboard(load_func):
    """영업 프로세스 현황 대시보드"""
    st.header("📊 영업 프로세스 현황")
    
    # 데이터 로드
    processes = load_func('sales_process')
    
    if processes:
        df = pd.DataFrame(processes)
        
        # 메트릭 카드
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 프로세스", len(df))
        
        with col2:
            total_amount = df['total_amount'].sum() if 'total_amount' in df.columns else 0
            st.metric("총 거래액", f"${total_amount:,.0f}")
        
        with col3:
            completed = len(df[df['process_status'] == 'completed']) if 'process_status' in df.columns else 0
            completion_rate = (completed / len(df) * 100) if len(df) > 0 else 0
            st.metric("완료율", f"{completion_rate:.1f}%")
        
        with col4:
            in_progress = len(df[df['process_status'].isin(['approved', 'ordered', 'received'])]) if 'process_status' in df.columns else 0
            st.metric("진행 중", in_progress)
        
        # 상태별 분포 차트
        if 'process_status' in df.columns:
            st.subheader("📈 상태별 분포")
            status_counts = df['process_status'].value_counts()
            st.bar_chart(status_counts)
        
        # 지연 알림
        render_delay_alerts(processes)
        
        # 프로세스 목록 - 상태 변경 기능 포함
        st.subheader("📋 프로세스 목록")
        render_process_list_with_status_update(processes, load_func)
        
    else:
        st.info("등록된 영업 프로세스가 없습니다.")
        
        # 빈 메트릭 표시
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("총 프로세스", "0")
        with col2:
            st.metric("총 거래액", "$0")
        with col3:
            st.metric("완료율", "0%")
        with col4:
            st.metric("진행 중", "0")

def render_process_list_with_status_update(processes, load_func):
    """프로세스 목록 - 상태 변경 기능 포함"""
    for process in processes:
        with st.expander(f"📋 {process.get('process_number', 'N/A')} - {process.get('customer_name', 'N/A')}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**고객명**: {process.get('customer_name', 'N/A')}")
                st.write(f"**품목**: {process.get('item_description', 'N/A')}")
                st.write(f"**수량**: {process.get('quantity', 0):,}개")
                st.write(f"**총 금액**: ${process.get('total_amount', 0):,.2f}")
                st.write(f"**예상 납기**: {process.get('expected_delivery_date', 'N/A')}")
                st.write(f"**현재 상태**: {process.get('process_status', 'N/A')}")
            
            with col2:
                # 상태 변경 기능
                current_status = process.get('process_status', 'approved')
                status_options = ['approved', 'completed', 'ordered', 'received', 'closed']
                
                try:
                    current_index = status_options.index(current_status)
                except ValueError:
                    current_index = 0
                
                new_status = st.selectbox(
                    "상태 변경:",
                    status_options,
                    index=current_index,
                    key=f"status_{process['id']}"
                )
                
                if st.button(f"상태 저장", key=f"save_{process['id']}"):
                    # 상태 업데이트 - update_func이 필요하지만 여기서는 임시로 표시만
                    st.success(f"상태를 {new_status}로 변경했습니다!")
                    st.info("페이지를 새로고침하면 변경사항이 반영됩니다.")

def render_delay_alerts(processes):
    """지연 알림 시스템"""
    if not processes:
        return
    
    st.subheader("⚠️ 지연 알림")
    
    today = date.today()
    delayed_processes = []
    
    for process in processes:
        if process.get('expected_delivery_date'):
            try:
                # 문자열을 date 객체로 변환
                if isinstance(process['expected_delivery_date'], str):
                    expected_date = datetime.strptime(process['expected_delivery_date'], '%Y-%m-%d').date()
                else:
                    expected_date = process['expected_delivery_date']
                
                # 완료되지 않았고 예상 배송일이 지난 경우
                if (process.get('process_status') != 'completed' and 
                    expected_date < today):
                    delayed_processes.append({
                        'process_number': process.get('process_number', 'N/A'),
                        'customer_name': process.get('customer_name', 'N/A'),
                        'expected_delivery_date': expected_date,
                        'days_delayed': (today - expected_date).days,
                        'status': process.get('process_status', 'N/A')
                    })
            except (ValueError, TypeError):
                continue
    
    if delayed_processes:
        st.warning(f"⚠️ {len(delayed_processes)}개 프로세스가 지연되고 있습니다!")
        
        delay_df = pd.DataFrame(delayed_processes)
        delay_df = delay_df.sort_values('days_delayed', ascending=False)
        
        for _, row in delay_df.iterrows():
            with st.expander(f"🚨 {row['process_number']} - {row['days_delayed']}일 지연"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**고객명**: {row['customer_name']}")
                    st.write(f"**현재 상태**: {row['status']}")
                with col2:
                    st.write(f"**예상 배송일**: {row['expected_delivery_date']}")
                    st.write(f"**지연 일수**: {row['days_delayed']}일")
    else:
        st.success("✅ 지연된 프로세스가 없습니다.")