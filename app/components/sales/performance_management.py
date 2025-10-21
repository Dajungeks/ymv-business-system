"""
실적 관리 시스템
- 견적번호로 검색 (Approved 상태만)
- 인보이스 번호 입력
- 실제 물류비 입력
- 실제 마진 자동 계산
- 상태 변경: Completed
"""

import streamlit as st
import pandas as pd
from datetime import datetime


def show_performance_management(load_func, update_func):
    """실적 관리 메인 페이지"""
    st.title("📊 실적 관리")
    
    tab1, tab2 = st.tabs(["실적 입력", "실적 목록"])
    
    with tab1:
        render_performance_input(load_func, update_func)
    
    with tab2:
        render_performance_list(load_func)


def render_performance_input(load_func, update_func):
    """실적 입력 폼"""
    st.header("📝 실적 입력")
    
    st.info("💡 Approved 상태의 견적서만 실적 입력이 가능합니다.")
    
    # Step 1: 견적서 검색
    st.subheader("Step 1: 견적서 검색")
    
    try:
        quotations_data = load_func('quotations')
        
        if not quotations_data:
            st.warning("등록된 견적서가 없습니다.")
            return
        
        quotations_df = pd.DataFrame(quotations_data)
        
        # Approved 상태만 필터링
        approved_quotations = quotations_df[quotations_df['status'] == 'Approved'].copy()
        
        if approved_quotations.empty:
            st.warning("⚠️ Approved 상태의 견적서가 없습니다.")
            return
        
        # 고객명 매핑
        customers_data = load_func('customers')
        if customers_data:
            customers_df = pd.DataFrame(customers_data)
            customer_dict = {}
            for _, row in customers_df.iterrows():
                display_name = row.get('company_name_short') or row.get('company_name_original')
                customer_dict[row['id']] = display_name
            approved_quotations['customer_company'] = approved_quotations['customer_id'].map(customer_dict).fillna(approved_quotations['customer_name'])
        else:
            approved_quotations['customer_company'] = approved_quotations['customer_name']
        
        # 검색 필터
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_term = st.text_input("검색", placeholder="견적번호 또는 고객사명", key="perf_search")
        
        with col2:
            st.write("")
            st.write("")
            search_btn = st.button("🔍 검색", use_container_width=True, type="primary")
        
        # 필터링
        if search_term:
            filtered = approved_quotations[
                approved_quotations['quote_number'].str.contains(search_term, case=False, na=False) |
                approved_quotations['customer_company'].str.contains(search_term, case=False, na=False)
            ]
        else:
            filtered = approved_quotations
        
        st.markdown("---")
        
        # 견적서 목록 표시
        if not filtered.empty:
            st.info(f"📋 {len(filtered)}개 견적서 검색됨")
            
            table_data = []
            for _, row in filtered.iterrows():
                table_data.append({
                    'ID': row.get('id', ''),
                    '견적번호': row.get('quote_number', ''),
                    'Rev': row.get('revision_number', 'Rv00'),
                    '고객사': row.get('customer_company', ''),
                    '제품': row.get('item_name_vn', ''),
                    '수량': f"{row.get('quantity', 0):,}",
                    '금액': f"{row.get('final_amount', 0):,.0f}",
                    '견적일': row.get('quote_date', '')
                })
            
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            # Step 2: 견적서 선택
            st.subheader("Step 2: 실적 입력")
            
            col1, col2, col3 = st.columns([3, 1, 3])
            
            with col1:
                quotation_id_input = st.text_input("견적서 ID", placeholder="ID 입력", key="perf_quot_id")
            
            with col2:
                if st.button("➡️ 선택", use_container_width=True, type="primary"):
                    if quotation_id_input and quotation_id_input.strip().isdigit():
                        quotation_id = int(quotation_id_input.strip())
                        selected = filtered[filtered['id'] == quotation_id]
                        
                        if not selected.empty:
                            st.session_state.selected_quotation_for_performance = selected.iloc[0].to_dict()
                            st.rerun()
                        else:
                            st.error(f"❌ ID {quotation_id}를 찾을 수 없습니다.")
                    else:
                        st.error("❌ 올바른 ID를 입력하세요.")
            
            # 선택된 견적서 실적 입력 폼
            if st.session_state.get('selected_quotation_for_performance'):
                render_performance_form(update_func)
        else:
            st.warning("⚠️ 검색 결과가 없습니다.")
    
    except Exception as e:
        st.error(f"❌ 견적서 로드 중 오류: {str(e)}")


def render_performance_form(update_func):
    """실적 입력 폼"""
    quotation = st.session_state.selected_quotation_for_performance
    
    st.markdown("---")
    st.success(f"✅ 선택된 견적서: **{quotation.get('quote_number')}** - {quotation.get('customer_company', '')}")
    
    # 견적서 정보 표시
    with st.expander("📋 견적서 정보", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("견적번호", quotation.get('quote_number', ''))
            st.metric("고객사", quotation.get('customer_company', ''))
            st.metric("제품", quotation.get('item_name_vn', ''))
        
        with col2:
            st.metric("수량", f"{quotation.get('quantity', 0):,}개")
            st.metric("견적금액", f"{quotation.get('final_amount', 0):,.0f} VND")
            st.metric("견적일", quotation.get('quote_date', ''))
        
        with col3:
            # 예상 물류비 정보
            estimated_logistics = quotation.get('estimated_logistics_total', 0)
            estimated_margin = quotation.get('estimated_margin_rate', 0)
            
            st.metric("예상 물류비", f"${estimated_logistics:,.2f}" if estimated_logistics else "미설정")
            st.metric("예상 마진율", f"{estimated_margin:.1f}%" if estimated_margin else "미설정")
    
    st.markdown("---")
    
    # 실적 입력 폼
    with st.form("performance_form"):
        st.subheader("📝 실적 정보 입력")
        
        col1, col2 = st.columns(2)
        
        with col1:
            invoice_number = st.text_input(
                "인보이스 번호 *",
                placeholder="예: INV-2025-001",
                value=quotation.get('invoice_number', '') or ''
            )
            st.caption("외부 인보이스 시스템에서 발행된 번호를 입력하세요.")
        
        with col2:
            actual_logistics_cost = st.number_input(
                "실제 물류비 (USD) *",
                min_value=0.0,
                value=float(quotation.get('actual_logistics_cost', 0)) if quotation.get('actual_logistics_cost') else 0.0,
                step=10.0,
                format="%.2f"
            )
            st.caption("실제 발생한 물류비를 입력하세요.")
        
        # 실제 마진 계산
        quantity = quotation.get('quantity', 1)
        cost_price_usd = quotation.get('cost_price_usd', 0)
        discounted_price_usd = quotation.get('discounted_price_usd', 0)
        exchange_rate = quotation.get('exchange_rate', 26387.45)
        
        if actual_logistics_cost > 0 and quantity > 0:
            actual_logistics_per_unit = actual_logistics_cost / quantity
            actual_total_cost = cost_price_usd + actual_logistics_per_unit
            
            if discounted_price_usd > 0:
                actual_margin = ((discounted_price_usd - actual_total_cost) / discounted_price_usd) * 100
                actual_margin_amount_usd = discounted_price_usd - actual_total_cost
                actual_margin_amount_vnd = actual_margin_amount_usd * exchange_rate
                
                st.markdown("---")
                st.subheader("📊 실제 마진 계산")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.info(f"📦 개당 물류비\n${actual_logistics_per_unit:.2f}")
                
                with col2:
                    st.info(f"💵 총 비용\n${actual_total_cost:.2f}")
                
                with col3:
                    if actual_margin > 0:
                        st.success(f"📈 실제 마진율\n{actual_margin:.1f}%")
                    else:
                        st.error(f"📉 손실\n{abs(actual_margin):.1f}%")
                
                st.caption(f"💰 마진 금액: ${actual_margin_amount_usd:,.2f} USD = {actual_margin_amount_vnd:,.0f} VND")
                
                # 예상 vs 실제 비교
                if quotation.get('estimated_margin_rate'):
                    estimated_margin = float(quotation.get('estimated_margin_rate'))
                    margin_diff = actual_margin - estimated_margin
                    
                    st.markdown("---")
                    st.subheader("📉 예상 vs 실제 비교")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("예상 마진", f"{estimated_margin:.1f}%")
                    
                    with col2:
                        st.metric("실제 마진", f"{actual_margin:.1f}%")
                    
                    with col3:
                        st.metric("차이", f"{margin_diff:+.1f}%", delta=f"{margin_diff:+.1f}%")
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            submitted = st.form_submit_button("💾 저장 및 완료 처리", type="primary", use_container_width=True)
        
        with col2:
            cancel = st.form_submit_button("❌ 취소", use_container_width=True)
        
        if cancel:
            st.session_state.pop('selected_quotation_for_performance', None)
            st.rerun()
        
        if submitted:
            if not invoice_number.strip():
                st.error("❌ 인보이스 번호를 입력해주세요.")
                return
            
            if actual_logistics_cost <= 0:
                st.error("❌ 실제 물류비를 입력해주세요.")
                return
            
            # 실제 마진 계산
            actual_logistics_per_unit = actual_logistics_cost / quantity if quantity > 0 else 0
            actual_total_cost = cost_price_usd + actual_logistics_per_unit
            actual_margin_rate = None
            
            if discounted_price_usd > 0:
                actual_margin_rate = ((discounted_price_usd - actual_total_cost) / discounted_price_usd) * 100
            
            # 업데이트 데이터
            update_data = {
                'id': quotation.get('id'),
                'invoice_number': invoice_number.strip(),
                'actual_logistics_cost': actual_logistics_cost,
                'actual_margin_rate': actual_margin_rate,
                'status': 'Completed',
                'updated_at': datetime.now().isoformat()
            }
            
            try:
                if update_func('quotations', update_data):
                    st.success("✅ 실적이 성공적으로 저장되었습니다!")
                    st.success("✅ 견적서 상태가 'Completed'로 변경되었습니다!")
                    st.balloons()
                    
                    st.session_state.pop('selected_quotation_for_performance', None)
                    st.rerun()
                else:
                    st.error("❌ 저장 실패")
            except Exception as e:
                st.error(f"❌ 저장 중 오류: {str(e)}")


def render_performance_list(load_func):
    """실적 목록"""
    st.header("📋 실적 목록")
    
    try:
        quotations_data = load_func('quotations')
        
        if not quotations_data:
            st.info("등록된 견적서가 없습니다.")
            return
        
        quotations_df = pd.DataFrame(quotations_data)
        
        # Completed 상태만 필터링
        completed_quotations = quotations_df[quotations_df['status'] == 'Completed'].copy()
        
        if completed_quotations.empty:
            st.info("완료된 실적이 없습니다.")
            return
        
        # 고객명 매핑
        customers_data = load_func('customers')
        if customers_data:
            customers_df = pd.DataFrame(customers_data)
            customer_dict = {}
            for _, row in customers_df.iterrows():
                display_name = row.get('company_name_short') or row.get('company_name_original')
                customer_dict[row['id']] = display_name
            completed_quotations['customer_company'] = completed_quotations['customer_id'].map(customer_dict).fillna(completed_quotations['customer_name'])
        else:
            completed_quotations['customer_company'] = completed_quotations['customer_name']
        
        # 검색 필터
        st.markdown("### 🔍 검색")
        col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 1])
        
        with col1:
            search_term = st.text_input("검색", placeholder="견적번호/인보이스번호/고객사명", key="perf_list_search")
        
        with col2:
            date_filter = st.selectbox("기간", ["전체", "이번달", "지난달", "올해"], key="perf_date_filter")
        
        with col3:
            margin_filter = st.selectbox("마진", ["전체", "양호(10%↑)", "보통(5~10%)", "낮음(5%↓)", "손실"], key="perf_margin_filter")
        
        with col4:
            st.write("")
            st.write("")
            if st.button("📥 CSV", use_container_width=True):
                csv_data = generate_performance_csv(completed_quotations)
                st.download_button(
                    "다운로드",
                    csv_data,
                    f"performance_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )
        
        st.markdown("---")
        
        # 필터링
        filtered = completed_quotations.copy()
        
        if search_term:
            filtered = filtered[
                filtered['quote_number'].str.contains(search_term, case=False, na=False) |
                filtered['invoice_number'].str.contains(search_term, case=False, na=False) |
                filtered['customer_company'].str.contains(search_term, case=False, na=False)
            ]
        
        # 날짜 필터
        if date_filter != "전체":
            today = datetime.now().date()
            
            if date_filter == "이번달":
                month_start = today.replace(day=1)
                filtered = filtered[pd.to_datetime(filtered['quote_date']).dt.date >= month_start]
            elif date_filter == "지난달":
                if today.month == 1:
                    last_month_start = today.replace(year=today.year-1, month=12, day=1)
                    last_month_end = today.replace(year=today.year, month=1, day=1)
                else:
                    last_month_start = today.replace(month=today.month-1, day=1)
                    last_month_end = today.replace(month=today.month, day=1)
                filtered = filtered[
                    (pd.to_datetime(filtered['quote_date']).dt.date >= last_month_start) &
                    (pd.to_datetime(filtered['quote_date']).dt.date < last_month_end)
                ]
            elif date_filter == "올해":
                year_start = today.replace(month=1, day=1)
                filtered = filtered[pd.to_datetime(filtered['quote_date']).dt.date >= year_start]
        
        # 마진 필터
        if margin_filter != "전체":
            if margin_filter == "양호(10%↑)":
                filtered = filtered[filtered['actual_margin_rate'] >= 10]
            elif margin_filter == "보통(5~10%)":
                filtered = filtered[(filtered['actual_margin_rate'] >= 5) & (filtered['actual_margin_rate'] < 10)]
            elif margin_filter == "낮음(5%↓)":
                filtered = filtered[(filtered['actual_margin_rate'] >= 0) & (filtered['actual_margin_rate'] < 5)]
            elif margin_filter == "손실":
                filtered = filtered[filtered['actual_margin_rate'] < 0]
        
        # 테이블 표시
        if not filtered.empty:
            table_data = []
            for _, row in filtered.iterrows():
                actual_margin = row.get('actual_margin_rate', 0)
                estimated_margin = row.get('estimated_margin_rate', 0)
                
                # 마진 상태 아이콘
                if actual_margin >= 10:
                    margin_status = "🟢"
                elif actual_margin >= 5:
                    margin_status = "🟡"
                elif actual_margin >= 0:
                    margin_status = "🟠"
                else:
                    margin_status = "🔴"
                
                table_data.append({
                    'ID': row.get('id', ''),
                    '견적번호': row.get('quote_number', ''),
                    '인보이스': row.get('invoice_number', ''),
                    '고객사': row.get('customer_company', ''),
                    '제품': row.get('item_name_vn', ''),
                    '수량': f"{row.get('quantity', 0):,}",
                    '금액': f"{row.get('final_amount', 0):,.0f}",
                    '예상마진': f"{estimated_margin:.1f}%" if estimated_margin else "N/A",
                    '실제마진': f"{margin_status} {actual_margin:.1f}%" if actual_margin is not None else "N/A",
                    '견적일': row.get('quote_date', '')
                })
            
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.caption(f"📊 총 **{len(filtered)}개** 실적")
            
            # 통계 요약
            st.markdown("---")
            st.subheader("📈 실적 요약")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_amount = filtered['final_amount'].fillna(0).sum()
                st.metric("총 매출", f"{total_amount:,.0f} VND")
            
            with col2:
                avg_margin = filtered['actual_margin_rate'].mean()
                st.metric("평균 마진율", f"{avg_margin:.1f}%")
            
            with col3:
                positive_margin = len(filtered[filtered['actual_margin_rate'] > 0])
                success_rate = (positive_margin / len(filtered) * 100) if len(filtered) > 0 else 0
                st.metric("수익률", f"{success_rate:.1f}%")
            
            with col4:
                completed_count = len(filtered)
                st.metric("완료 건수", f"{completed_count}건")
        else:
            st.info("조건에 맞는 실적이 없습니다.")
    
    except Exception as e:
        st.error(f"❌ 실적 목록 로드 중 오류: {str(e)}")


def generate_performance_csv(performance_df):
    """실적 CSV 생성"""
    csv_data = []
    for _, row in performance_df.iterrows():
        csv_data.append({
            'id': row.get('id', ''),
            'quote_number': row.get('quote_number', ''),
            'invoice_number': row.get('invoice_number', ''),
            'customer': row.get('customer_company', ''),
            'item': row.get('item_name_vn', ''),
            'quantity': row.get('quantity', 0),
            'amount': row.get('final_amount', 0),
            'estimated_margin': row.get('estimated_margin_rate', 0),
            'actual_margin': row.get('actual_margin_rate', 0),
            'date': row.get('quote_date', '')
        })
    
    df = pd.DataFrame(csv_data)
    return df.to_csv(index=False, encoding='utf-8-sig')