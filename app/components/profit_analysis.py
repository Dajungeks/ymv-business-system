import streamlit as st
import pandas as pd

def show_profit_analysis(load_func):
    """수익 분석 및 통계"""
    st.header("💰 수익 분석")
    
    # 데이터 로드
    try:
        # 분석 뷰 데이터 로드
        analysis_data = load_func('sales_process_analysis')
        
        if not analysis_data:
            # 뷰가 없거나 데이터가 없는 경우 기본 테이블에서 계산
            st.warning("sales_process_analysis 뷰에서 데이터를 가져올 수 없습니다. 기본 테이블에서 분석합니다.")
            analysis_data = calculate_profit_from_base_tables(load_func)
        
        if analysis_data:
            render_profit_dashboard(analysis_data)
        else:
            render_empty_dashboard()
            
    except Exception as e:
        st.error(f"데이터 로드 중 오류가 발생했습니다: {str(e)}")
        render_empty_dashboard()

def calculate_profit_from_base_tables(load_func):
    """기본 테이블에서 수익 분석 데이터 계산"""
    try:
        # 영업 프로세스 데이터
        processes = load_func('sales_process') or []
        # 고객 주문 발주 데이터
        customer_orders = load_func('purchase_orders_to_supplier') or []
        
        analysis_data = []
        
        for process in processes:
            # 해당 프로세스의 발주 비용 찾기
            related_orders = [
                order for order in customer_orders 
                if order.get('sales_process_id') == process.get('id')
            ]
            
            # 총 발주 비용 계산 (USD)
            total_supplier_cost = sum(
                float(order.get('total_cost', 0)) for order in related_orders
            )
            
            # 고객 매출 (VND)
            customer_amount_vnd = float(process.get('total_amount', 0))
            
            # 환율 적용 (VND → USD, 임시 환율 24,000)
            exchange_rate = 24000
            customer_amount_usd = customer_amount_vnd / exchange_rate if customer_amount_vnd > 0 else 0
            
            # 수익률 계산
            if customer_amount_usd > 0:
                profit_margin = ((customer_amount_usd - total_supplier_cost) / customer_amount_usd) * 100
            else:
                profit_margin = 0
            
            analysis_data.append({
                'process_number': process.get('process_number', 'N/A'),
                'customer_name': process.get('customer_name', 'N/A'),
                'customer_amount_vnd': customer_amount_vnd,
                'customer_amount_usd': customer_amount_usd,
                'supplier_cost_usd': total_supplier_cost,
                'profit_usd': customer_amount_usd - total_supplier_cost,
                'profit_margin_percent': profit_margin,
                'process_status': process.get('process_status', 'N/A')
            })
        
        return analysis_data
        
    except Exception as e:
        st.error(f"수익 분석 계산 중 오류: {str(e)}")
        return []

def render_profit_dashboard(analysis_data):
    """수익 분석 대시보드 렌더링"""
    df = pd.DataFrame(analysis_data)
    
    # 메트릭 카드
    st.subheader("📊 전체 수익 현황")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue_usd = df['customer_amount_usd'].sum()
        st.metric("총 매출 (USD)", f"${total_revenue_usd:,.0f}")
    
    with col2:
        total_cost_usd = df['supplier_cost_usd'].sum()
        st.metric("총 원가 (USD)", f"${total_cost_usd:,.0f}")
    
    with col3:
        total_profit_usd = df['profit_usd'].sum()
        st.metric("총 수익 (USD)", f"${total_profit_usd:,.0f}")
    
    with col4:
        avg_margin = df['profit_margin_percent'].mean() if len(df) > 0 else 0
        st.metric("평균 수익률", f"{avg_margin:.1f}%")
    
    # 환율 정보
    st.info("💱 적용 환율: 1 USD = 24,000 VND (고정값, 실제 환율과 다를 수 있음)")
    
    # 수익률 분포 차트
    if len(df) > 0:
        st.subheader("📈 수익률 분포")
        
        # 수익률 구간별 분류
        df['profit_category'] = df['profit_margin_percent'].apply(categorize_profit_margin)
        profit_distribution = df['profit_category'].value_counts()
        
        if not profit_distribution.empty:
            st.bar_chart(profit_distribution)
        
        # 상위/하위 수익률 프로젝트
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 상위 수익률 프로젝트")
            top_profits = df.nlargest(5, 'profit_margin_percent')[['process_number', 'customer_name', 'profit_margin_percent', 'profit_usd']]
            if not top_profits.empty:
                for _, row in top_profits.iterrows():
                    st.write(f"**{row['process_number']}** - {row['customer_name']}")
                    st.write(f"   수익률: {row['profit_margin_percent']:.1f}%, 수익: ${row['profit_usd']:,.0f}")
            else:
                st.info("데이터가 없습니다.")
        
        with col2:
            st.subheader("⚠️ 낮은 수익률 프로젝트")
            low_profits = df.nsmallest(5, 'profit_margin_percent')[['process_number', 'customer_name', 'profit_margin_percent', 'profit_usd']]
            if not low_profits.empty:
                for _, row in low_profits.iterrows():
                    st.write(f"**{row['process_number']}** - {row['customer_name']}")
                    st.write(f"   수익률: {row['profit_margin_percent']:.1f}%, 수익: ${row['profit_usd']:,.0f}")
            else:
                st.info("데이터가 없습니다.")
    
    # 프로젝트별 수익률 테이블
    st.subheader("📋 프로젝트별 수익 분석")
    
    # 필터링 옵션
    col1, col2 = st.columns(2)
    
    with col1:
        status_filter = st.multiselect(
            "상태별 필터:",
            options=df['process_status'].unique() if len(df) > 0 else [],
            default=df['process_status'].unique() if len(df) > 0 else []
        )
    
    with col2:
        margin_filter = st.slider(
            "최소 수익률 (%)",
            min_value=float(df['profit_margin_percent'].min()) if len(df) > 0 else 0.0,
            max_value=float(df['profit_margin_percent'].max()) if len(df) > 0 else 100.0,
            value=float(df['profit_margin_percent'].min()) if len(df) > 0 else 0.0
        )
    
    # 필터 적용
    if len(df) > 0:
        filtered_df = df[
            (df['process_status'].isin(status_filter)) & 
            (df['profit_margin_percent'] >= margin_filter)
        ]
    else:
        filtered_df = df
    
    # 표시할 컬럼 선택
    display_columns = [
        'process_number', 'customer_name', 'customer_amount_vnd', 
        'customer_amount_usd', 'supplier_cost_usd', 'profit_usd', 
        'profit_margin_percent', 'process_status'
    ]
    
    if len(filtered_df) > 0:
        # 데이터 포맷팅
        display_df = filtered_df[display_columns].copy()
        display_df['customer_amount_vnd'] = display_df['customer_amount_vnd'].apply(lambda x: f"{x:,.0f} VND")
        display_df['customer_amount_usd'] = display_df['customer_amount_usd'].apply(lambda x: f"${x:,.0f}")
        display_df['supplier_cost_usd'] = display_df['supplier_cost_usd'].apply(lambda x: f"${x:,.0f}")
        display_df['profit_usd'] = display_df['profit_usd'].apply(lambda x: f"${x:,.0f}")
        display_df['profit_margin_percent'] = display_df['profit_margin_percent'].apply(lambda x: f"{x:.1f}%")
        
        # 컬럼명 한국어로 변경
        display_df.columns = [
            '프로세스번호', '고객명', '매출(VND)', '매출(USD)', 
            '원가(USD)', '수익(USD)', '수익률(%)', '상태'
        ]
        
        st.dataframe(display_df, use_container_width=True)
        
        # 요약 정보
        st.subheader("📊 필터링된 데이터 요약")
        summary_col1, summary_col2, summary_col3 = st.columns(3)
        
        with summary_col1:
            st.metric("프로젝트 수", len(filtered_df))
        with summary_col2:
            filtered_revenue = filtered_df['customer_amount_usd'].sum()
            st.metric("필터된 총 매출", f"${filtered_revenue:,.0f}")
        with summary_col3:
            filtered_profit = filtered_df['profit_usd'].sum()
            st.metric("필터된 총 수익", f"${filtered_profit:,.0f}")
    else:
        st.info("필터 조건에 맞는 데이터가 없습니다.")
    
    # 월별 수익 추이 (생성일 기준)
    if len(df) > 0:
        st.subheader("📈 시기별 수익 추이")
        try:
            # 간단한 월별 집계 (실제로는 created_at 필드 필요)
            monthly_profit = df.groupby('process_status').agg({
                'profit_usd': 'sum',
                'profit_margin_percent': 'mean'
            }).round(2)
            
            if not monthly_profit.empty:
                st.write("**상태별 수익 집계**")
                st.dataframe(monthly_profit)
        except Exception as e:
            st.info("월별 추이 분석을 위해서는 추가 데이터가 필요합니다.")

def render_empty_dashboard():
    """데이터가 없을 때의 대시보드"""
    st.subheader("📊 전체 수익 현황")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 매출 (USD)", "$0")
    with col2:
        st.metric("총 원가 (USD)", "$0")
    with col3:
        st.metric("총 수익 (USD)", "$0")
    with col4:
        st.metric("평균 수익률", "0%")
    
    st.info("분석할 수 있는 영업 프로세스 데이터가 없습니다.")
    st.write("💡 **수익 분석을 위해 필요한 데이터:**")
    st.write("- 완료된 영업 프로세스")
    st.write("- 해당 프로세스의 발주 데이터")
    st.write("- 정확한 원가 정보")

def categorize_profit_margin(margin):
    """수익률을 카테고리로 분류"""
    if margin >= 30:
        return "높음 (30%+)"
    elif margin >= 15:
        return "보통 (15-30%)"
    elif margin >= 0:
        return "낮음 (0-15%)"
    else:
        return "손실 (음수)"

# 환율 관련 유틸리티 함수들
def get_exchange_rate():
    """환율 정보 반환 (향후 실시간 API 연동 가능)"""
    # 임시 고정 환율
    return {
        'USD_to_VND': 24000,
        'VND_to_USD': 1/24000,
        'last_updated': '2025-09-28'
    }

def convert_currency(amount, from_currency, to_currency):
    """통화 변환"""
    rates = get_exchange_rate()
    
    if from_currency == 'VND' and to_currency == 'USD':
        return amount * rates['VND_to_USD']
    elif from_currency == 'USD' and to_currency == 'VND':
        return amount * rates['USD_to_VND']
    else:
        return amount  # 같은 통화인 경우