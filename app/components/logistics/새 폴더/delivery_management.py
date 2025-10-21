import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.database_logistics import (
    get_all_providers,
    get_delivery_statistics,
    get_provider_delivery_stats,
    get_top_delay_causes,
    get_delayed_logistics,
    get_section_analysis
)

def delivery_management_page():
    """납기 관리 및 지연 분석 페이지"""
    st.title("📅 납기 관리 및 지연 분석")
    
    tab1, tab2, tab3 = st.tabs(["대시보드", "지연 건 상세", "구간별 분석"])
    
    with tab1:
        show_delivery_dashboard()
    
    with tab2:
        show_delayed_items()
    
    with tab3:
        show_section_analysis()


def show_delivery_dashboard():
    """납기 대시보드"""
    st.subheader("📊 납기 준수율 대시보드")
    
    # 기간 선택
    col1, col2 = st.columns(2)
    with col1:
        period = st.selectbox("기간", ["이번 달", "최근 3개월", "최근 6개월", "올해"], key="dashboard_period")
    with col2:
        provider_filter = st.selectbox("물류사", ["전체"] + get_all_providers(), key="dashboard_provider")
    
    # 통계 데이터 조회
    stats = get_delivery_statistics(period, provider_filter)
    
    # 상단 메트릭
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("전체 건수", f"{stats['total']}건")
    
    with col2:
        on_time_rate = (stats['on_time'] / stats['total'] * 100) if stats['total'] > 0 else 0
        st.metric("정시율", f"{on_time_rate:.1f}%", 
                 delta=f"{stats['rate_change']:+.1f}%" if stats['rate_change'] else None)
    
    with col3:
        st.metric("평균 지연", f"{stats['avg_delay']:.1f}일")
    
    with col4:
        st.metric("최대 지연", f"{stats['max_delay']}일")
    
    st.divider()
    
    # 심각도별 현황
    st.subheader("📈 심각도별 현황")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        on_time_pct = (stats['on_time']/stats['total']*100) if stats['total'] > 0 else 0
        st.markdown(f"""
        ### ✅ 정시
        **{stats['on_time']}건** ({on_time_pct:.0f}%)
        """)

    with col2:
        minor_pct = (stats['minor']/stats['total']*100) if stats['total'] > 0 else 0
        st.markdown(f"""
        ### ⚠️ 경미
        **{stats['minor']}건** ({minor_pct:.0f}%)
        1-2일 지연
        """)

    with col3:
        major_pct = (stats['major']/stats['total']*100) if stats['total'] > 0 else 0
        st.markdown(f"""
        ### 🔴 중대
        **{stats['major']}건** ({major_pct:.0f}%)
        3-5일 지연
        """)

    with col4:
        critical_pct = (stats['critical']/stats['total']*100) if stats['total'] > 0 else 0
        st.markdown(f"""
        ### 🔴 심각
        **{stats['critical']}건** ({critical_pct:.0f}%)
        5일 초과
        """)
    
    st.divider()
    
    # 물류사별 성과
    st.subheader("🏢 물류사별 납기 성과")
    
    provider_stats = get_provider_delivery_stats(period)
    
    if provider_stats:
        df = pd.DataFrame(provider_stats)
        
        st.dataframe(
            df,
            column_config={
                "provider": "물류사",
                "total": "전체 건",
                "on_time_rate": st.column_config.ProgressColumn(
                    "정시율",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100
                ),
                "avg_delay": "평균 지연 (일)",
                "reliability": "신뢰도"
            },
            hide_index=True,
            use_container_width=True
        )
    
    st.divider()
    
    # 지연 원인 분석
    st.subheader("📋 지연 원인 TOP 5")
    
    delay_causes = get_top_delay_causes(period, provider_filter)
    
    for idx, cause in enumerate(delay_causes, 1):
        severity_icon = "🔴" if cause['count'] >= 5 else "⚠️"
        st.markdown(f"""
        **{idx}. {severity_icon} {cause['reason_name']}**
        - 발생: {cause['count']}건
        - 평균 지연: {cause['avg_delay']:.1f}일
        - 책임: {cause['responsible']}
        """)
        st.progress(cause['count'] / delay_causes[0]['count'] if delay_causes else 0)


def show_delayed_items():
    """지연 건 상세 목록"""
    st.subheader("🔍 지연 건 상세 내역")
    
    # 필터
    col1, col2, col3 = st.columns(3)
    with col1:
        severity_filter = st.multiselect(
            "심각도",
            ["경미", "중대", "심각"],
            default=["중대", "심각"],
            key="delayed_severity"
        )
    
    with col2:
        provider_filter = st.selectbox("물류사", ["전체"] + get_all_providers(), key="delayed_provider")
    
    with col3:
        date_range = st.date_input(
            "기간",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            key="delayed_date"
        )
    
    # 지연 건 조회
    delayed_items = get_delayed_logistics(severity_filter, provider_filter, date_range)
    
    if not delayed_items:
        st.info("지연 건이 없습니다.")
        return
    
    # 목록 표시
    for item in delayed_items:
        with st.expander(f"🔴 {item['no']} - {item['provider']} ({item['shipping_date']})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                **기본 정보**
                - 출고일: {item['shipping_date']}
                - 예상 도착: {item['expected_arrival']}
                - 실제 도착: {item['actual_arrival']}
                - 지연: **{item['delay_days']}일** ({item['severity']})
                """)
            
            with col2:
                st.markdown(f"""
                **지연 정보**
                - 원인: {item['delay_reason']}
                - 책임: {item['responsible']}
                - 비용 영향: ${item['cost_impact']:.2f}
                """)
            
            st.markdown(f"""
            **상세 설명:**
            {item['delay_detail']}
            """)
            
            # 타임라인 버튼
            if st.button(f"📊 타임라인 보기", key=f"timeline_{item['id']}"):
                show_timeline_detail(item['id'])


def show_section_analysis():
    """구간별 분석"""
    st.subheader("📈 구간별 소요 시간 분석")
    
    # 기간 선택
    period = st.selectbox("분석 기간", ["최근 1개월", "최근 3개월", "최근 6개월"], key="section_period")
    
    # 구간별 데이터
    section_data = get_section_analysis(period)
    
    if not section_data:
        st.info("분석할 데이터가 없습니다.")
        return
    
    # 표 형태로 표시
    df = pd.DataFrame(section_data)
    
    st.dataframe(
        df,
        column_config={
            "section": "구간",
            "standard": "표준 시간 (일)",
            "actual": "실제 평균 (일)",
            "difference": "차이 (일)",
            "status": "상태"
        },
        hide_index=True,
        use_container_width=True
    )
    
    # 병목 구간 하이라이트
    bottleneck = max(section_data, key=lambda x: x['difference'])
    
    st.warning(f"""
    ⚠️ **가장 큰 병목 구간: {bottleneck['section']}**
    
    표준 대비 {bottleneck['difference']:.1f}일 초과 ({bottleneck['difference']/bottleneck['standard']*100:.0f}% 지연)
    
    개선이 필요합니다.
    """)
