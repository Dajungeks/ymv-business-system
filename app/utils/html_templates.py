"""
HTML 템플릿 관리 모듈
HTML Templates Management Module
"""

def get_quotation_html_template(quotation_data, sales_rep_data):
    """견적서 HTML 템플릿 생성"""
    
    # VAT 계산
    vat_rate = quotation_data.get('vat_rate', 10.0) / 100
    total_excl_vat = quotation_data.get('total_amount', 0)
    vat_amount = total_excl_vat * vat_rate
    total_incl_vat = total_excl_vat + vat_amount
    
    return f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Quotation - {quotation_data.get('quote_number', '')}-{quotation_data.get('revision_number', '')}</title>
        <style>
            {get_quotation_css()}
        </style>
    </head>
    <body>
        <div class="quotation">
            <div class="content-area">
                <!-- 헤더 -->
                <div class="header">
                    <!-- 고객 정보 영역 -->
                    <div>
                        <div class="company-name">{quotation_data.get('company', '[고객 회사명]')}</div>
                        <div class="company-info">
                            Address: {quotation_data.get('customer_address', '[고객 주소]')}<br><br>
                            Contact Person: {quotation_data.get('contact_person', '[고객 담당자]')}<br>
                            Phone No.: {quotation_data.get('phone', '[고객 전화번호]')}<br>
                            E-mail: {quotation_data.get('email', '[고객 이메일]')}
                        </div>
                    </div>
                    
                    <div>
                        <div class="company-name">YUMOLD VIETNAM CO., LTD</div>
                        <div class="company-info">
                            Tax Code (MST): 0111146237<br>
                            <div class="office-info">
                                <strong>Hanoi Accounting Office:</strong><br>
                                Room 1201-2, 12th Floor, Keangnam Hanoi Landmark 72, E6 Area,<br>
                                Yen Hoa Ward, Hanoi City
                            </div>
                            <div class="office-info">
                                <strong>Bac Ninh Sales Office:</strong><br>
                                6th Floor, No. 255 Le Thanh Tong Street, Vo Cuong Ward, Bac Ninh<br>
                                Province
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 견적 정보 -->
                <div class="quote-details">
                    <div>Date: {quotation_data.get('quote_date', '')}</div>
                    <div>Quote No.: {quotation_data.get('quote_number', '')}-{quotation_data.get('revision_number', '')}</div>
                    <div>Rev. No.: {quotation_data.get('revision_number', '')}</div>
                    <div>Currency: {quotation_data.get('currency', '')}</div>
                </div>
                
                <!-- 항목 테이블 -->
                <table>
                    <thead>
                        <tr>
                            <th style="width: 5%;">NO</th>
                            <th style="width: 12%;">Item Code</th>
                            <th style="width: 20%;">Item Name</th>
                            <th style="width: 6%;">Qty.</th>
                            <th style="width: 12%;">Std. Price</th>
                            <th style="width: 10%;">DC. Rate</th>
                            <th style="width: 12%;">Unit Price</th>
                            <th style="width: 12%;">Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td rowspan="3" style="vertical-align: top; padding-top: 25px;">1</td>
                            <td>{quotation_data.get('item_code', '')}</td>
                            <td>{quotation_data.get('item_name_en', '')}</td>
                            <td>{quotation_data.get('quantity', 0)}</td>
                            <td class="text-right">{quotation_data.get('std_price', 0):,.2f}</td>
                            <td>{quotation_data.get('discount_rate', 0):.2f}%</td>
                            <td class="text-right">{quotation_data.get('unit_price', 0):,.2f}</td>
                            <td class="text-right">{quotation_data.get('total_amount', 0):,.2f}</td>
                        </tr>
                        <tr>
                            <td colspan="7" style="padding: 8px; border-top: none; text-align: left;">
                                {quotation_data.get('remark', '')}
                            </td>
                        </tr>
                        <tr>
                            <td colspan="7" style="padding: 8px; border-top: none; text-align: left; font-style: italic; color: #666;">
                                [{quotation_data.get('item_name_vn', '')}]
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <!-- 하단 고정 영역 -->
            <div class="bottom-fixed">
                <!-- 합계 -->
                <div class="totals">
                    <table>
                        <tr>
                            <td class="text-right">TOTAL {quotation_data.get('currency', '')} Excl. VAT</td>
                            <td>{quotation_data.get('currency', '')}</td>
                            <td class="text-right">{total_excl_vat:,.2f}</td>
                        </tr>
                        <tr>
                            <td class="text-right">TOTAL {quotation_data.get('currency', '')} {quotation_data.get('vat_rate', 10):.1f}% VAT</td>
                            <td>{quotation_data.get('currency', '')}</td>
                            <td class="text-right">{vat_amount:,.2f}</td>
                        </tr>
                        <tr class="total-row">
                            <td class="text-right">TOTAL {quotation_data.get('currency', '')} Incl. VAT</td>
                            <td>{quotation_data.get('currency', '')}</td>
                            <td class="text-right">{total_incl_vat:,.2f}</td>
                        </tr>
                    </table>
                </div>
                
                <!-- 프로젝트 정보 -->
                <div class="project-info">
                    <table class="project-table">
                        <tr>
                            <td>Project Name:</td>
                            <td>{quotation_data.get('project_name', '')}</td>
                            <td>Part Name:</td>
                            <td>{quotation_data.get('part_name', '')}</td>
                        </tr>
                        <tr>
                            <td>Mold No.:</td>
                            <td>{quotation_data.get('mold_no', '')}</td>
                            <td>Part Weight:</td>
                            <td style="text-align: right;">{quotation_data.get('part_weight', 0):.1f}g</td>
                        </tr>
                        <tr>
                            <td>HRS Info:</td>
                            <td>{quotation_data.get('hrs_info', '')}</td>
                            <td>Resin Type:</td>
                            <td>{quotation_data.get('resin_type', '')}</td>
                        </tr>
                        <tr>
                            <td>Remark:</td>
                            <td>{quotation_data.get('remark', '')}</td>
                            <td>Valid Date:</td>
                            <td>{quotation_data.get('valid_until', '')}</td>
                        </tr>
                        <tr>
                            <td>Resin/Additive:</td>
                            <td>{quotation_data.get('resin_additive', '')}</td>
                            <td>Sales Rep:</td>
                            <td>{sales_rep_data.get('name', '')}</td>
                        </tr>
                        <tr>
                            <td>Sol/Material:</td>
                            <td>{quotation_data.get('sol_material', '')}</td>
                            <td>Contact:</td>
                            <td>{sales_rep_data.get('email', '')}</td>
                        </tr>
                        <tr>
                            <td>Payment Terms:</td>
                            <td>{quotation_data.get('payment_terms', '')}</td>
                            <td>Phone:</td>
                            <td>{sales_rep_data.get('phone', '')}</td>
                        </tr>
                        <tr>
                            <td>Delivery Date:</td>
                            <td>{quotation_data.get('delivery_date', '')}</td>
                            <td>Account:</td>
                            <td style="font-size: 10px;">700-038-038199 (Shinhan Bank Vietnam)</td>
                        </tr>
                    </table>
                </div>
                
                <!-- 공급업체 이름 -->
                <div style="text-align: center; margin: 30px 0; font-size: 16px; font-weight: bold;">
                    YUMOLD VIETNAM CO., LTD
                </div>
                
                <!-- 서명란 -->
                <div class="signature-section">
                    <div class="signature-box">
                        <div>Authorised Signature</div>
                        <div class="signature-line"></div>
                    </div>
                    <div class="signature-box">
                        <div>Customer Signature</div>
                        <div class="signature-line"></div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

def get_quotation_css():
    """견적서 CSS 스타일"""
    
    return """
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }
        
        .quotation {
            width: 210mm;
            min-height: 297mm;
            margin: 20px auto;
            background: white;
            padding: 15mm;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
        }
        
        .content-area {
            flex: 1;
        }
        
        .bottom-fixed {
            margin-top: auto;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #000;
        }
        
        .company-name {
            font-size: 18px;
            font-weight: bold;
        }
        
        .company-info {
            font-size: 12px;
            line-height: 1.4;
        }
        
        .quote-info {
            text-align: right;
            font-size: 12px;
        }
        
        .office-info {
            margin-top: 10px;
            font-size: 11px;
        }
        
        .quote-details {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
            font-size: 12px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            font-size: 11px;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }
        
        th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        
        .text-left {
            text-align: left;
        }
        
        .text-right {
            text-align: right;
        }
        
        .totals {
            margin-top: 20px;
        }
        
        .totals table {
            width: 300px;
            margin-left: auto;
        }
        
        .total-row {
            background-color: #e9ecef;
            font-weight: bold;
        }
        
        .project-info {
            margin-top: 30px;
            border-top: 1px solid #ddd;
            padding-top: 20px;
        }
        
        .project-table {
            width: 100%;
            font-size: 11px;
        }
        
        .project-table td {
            padding: 8px;
            border: 1px solid #ddd;
            vertical-align: middle;
        }
        
        .project-table td:nth-child(1) {
            width: 20%;
            font-weight: bold;
            background-color: #f8f9fa;
        }
        
        .project-table td:nth-child(2) {
            width: 30%;
        }
        
        .project-table td:nth-child(3) {
            width: 20%;
            font-weight: bold;
            background-color: #f8f9fa;
        }
        
        .project-table td:nth-child(4) {
            width: 30%;
        }
        
        .signature-section {
            margin-top: 40px;
            display: flex;
            justify-content: space-between;
        }
        
        .signature-box {
            text-align: center;
            width: 200px;
        }
        
        .signature-line {
            border-bottom: 1px solid #000;
            margin: 30px 0 10px 0;
            height: 1px;
        }
        
        @media print {
            body {
                background: white;
                margin: 0;
                padding: 0;
            }
            .quotation {
                width: 210mm;
                min-height: 297mm;
                margin: 0;
                padding: 15mm;
                box-shadow: none;
                page-break-after: always;
            }
            @page {
                size: A4;
                margin: 0;
            }
        }
    """

def get_purchase_order_html_template(po_data):
    """발주서 HTML 템플릿 생성"""
    # 향후 확장용
    pass

def get_invoice_html_template(invoice_data):
    """인보이스 HTML 템플릿 생성"""
    # 향후 확장용
    pass