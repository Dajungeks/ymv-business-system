import streamlit as st
import pandas as pd

def show_profit_analysis(load_func):
    """수익 분석"""
    
    st.subheader("💰 수익 분석")
    
    try:
        # sales_process_analysis 뷰에서 데이터 로드
        analysis_data = load_func("sales_process_analysis")
        
        if not analysis_data:
            st.info("분석할 데이터가 없습니다.")
            return
        
        # 전체 수익 통계
        total_sales_vnd = sum(float(item.get('customer_amount_vnd', 0)) for item in analysis_data if item.get('customer_amount_vnd'))
        total_cost_usd = sum(float(item.get('supplier_cost_usd', 0)) for item in analysis_data if item.get('supplier_cost_usd'))
        
        # 환율 적용 (간단한 고정 환율 사용)
        exchange_rate = 24000  # 1 USD = 24,000 VND
        total_sales_usd = total_sales_vnd / exchange_rate
        total_profit_usd = total_sales_usd - total_cost_usd
        profit_margin = (total_profit_usd / total_cost_usd * 100) if total_cost_usd > 0 else 0
        
        # 메트릭 표시
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 매출 (USD)", f"${total_sales_usd:,.0f}")
        with col2:
            st.metric("총 원가 (USD)", f"${total_cost_usd:,.0f}")
        with col3:
            st.metric("총 수익 (USD)", f"${total_profit_usd:,.0f}")
        with col4:
            st.metric("수익률", f"{profit_margin:.1f}%")
        
        # 프로젝트별 수익률 표
        st.write("### 📊 프로젝트별 수익 분석")
        
        profit_data = []
        for item in analysis_data:
            if item.get('supplier_cost_usd'):
                profit_data.append({
                    '프로세스 번호': item.get('process_number', 'N/A'),
                    '고객사': item.get('customer_name', 'N/A'),
                    '매출 (VND)': f"{float(item.get('customer_amount_vnd', 0)):,.0f}",
                    '원가 (USD)': f"${float(item.get('supplier_cost_usd', 0)):,.0f}",
                    '수익률 (%)': f"{float(item.get('profit_margin_percent', 0)):.1f}%"
                })
        
        if profit_data:
            df = pd.DataFrame(profit_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"수익 분석 중 오류 발생: {str(e)}")