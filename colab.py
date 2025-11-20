# ===================================================
#  BTCDetect Scientific Methodology (Google Colab Version)
#  Günther Zöeir INTERFACE - Bitcoin Transactions & BLOCKCHAIN MESSAGE
# ===================================================

import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
from secp256k1 import *
from sighash import *

def create_op_return_script(message):
    message_hex = message.encode('utf-8').hex()
    message_bytes = bytes.fromhex(message_hex)
    op_return_opcode = b'\x6a'
    data_length = len(message_bytes)
    if data_length <= 75:
        length_byte = bytes([data_length])
    elif data_length <= 255:
        length_byte = b'\x4c' + bytes([data_length])
    else:
        raise ValueError("Message is too long. Maximum allowed is 80 bytes for OP_RETURN.")

    return op_return_opcode + length_byte + message_bytes

def create_transaction_with_op_return(private_key_wif, utxo_txid, utxo_index,
                                      utxo_value, recipient_address,
                                      send_amount, message, fee=1000, testnet=True):
    pk = PrivateKey.parse(private_key_wif)

    tx_in = TxIn(bytes.fromhex(utxo_txid), utxo_index, b'', 0xffffffff)
    tx_in._script_pubkey = Tx.get_address_data(pk.address())['script_pubkey']
    tx_in._value = utxo_value
    tx_ins = [tx_in]

    # Calculate change (returned to sender)
    change_amount = utxo_value - send_amount - fee
    if change_amount < 0:
        raise ValueError("Insufficient funds to cover the amount and transaction fee.")

    # Transaction outputs
    tx_outs = []
    tx_outs.append(TxOut(0, create_op_return_script(message)))
    tx_outs.append(TxOut(send_amount, Tx.get_address_data(recipient_address)['script_pubkey'].serialize()))

    if change_amount > 546:  # dust limit
        tx_outs.append(TxOut(change_amount, Tx.get_address_data(pk.address())['script_pubkey'].serialize()))

    tx = Tx(1, tx_ins, tx_outs, 0, testnet=testnet)
    signature(tx, 0, pk)

    return tx, change_amount

# ===================================================
# CYBERPUNK DARKNET INTERFACE
# ===================================================

header_html = widgets.HTML("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');

    .btc-container {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a0a1f 50%, #0a0a0a 100%);
        border: 2px solid #00ff41;
        border-radius: 15px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 0 30px rgba(0, 255, 65, 0.3),
                    inset 0 0 50px rgba(0, 255, 65, 0.1);
        position: relative;
        overflow: hidden;
        font-family: 'Share Tech Mono', monospace;
    }

    .btc-container::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #00ff41, #00ffff, #ff00ff, #00ff41);
        border-radius: 15px;
        opacity: 0.2;
        z-index: -1;
        animation: borderGlow 3s linear infinite;
    }

    @keyframes borderGlow {
        0%, 100% { filter: hue-rotate(0deg); }
        50% { filter: hue-rotate(180deg); }
    }

    .btc-header {
        text-align: center;
        margin-bottom: 30px;
        position: relative;
    }

    .btc-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 42px;
        font-weight: 900;
        background: linear-gradient(90deg, #00ff41, #00ffff, #ff00ff, #00ff41);
        background-size: 300% 100%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientShift 4s ease infinite;
        text-shadow: 0 0 30px rgba(0, 255, 65, 0.8);
        letter-spacing: 3px;
        margin: 0;
        padding: 10px 0;
    }

    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    .btc-subtitle {
        font-family: 'Share Tech Mono', monospace;
        font-size: 14px;
        color: #00ff41;
        margin-top: 10px;
        opacity: 0.8;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .cyber-line {
        height: 2px;
        background: linear-gradient(90deg, transparent, #00ff41, transparent);
        margin: 20px 0;
        animation: pulse 2s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }

    .matrix-bg {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        opacity: 0.05;
        pointer-events: none;
        font-family: 'Share Tech Mono', monospace;
        font-size: 10px;
        color: #00ff41;
        line-height: 12px;
        overflow: hidden;
        z-index: 0;
    }

    .warning-badge {
        display: inline-block;
        background: rgba(255, 0, 255, 0.2);
        border: 1px solid #ff00ff;
        color: #ff00ff;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: bold;
        letter-spacing: 1px;
        margin-top: 10px;
        box-shadow: 0 0 15px rgba(255, 0, 255, 0.5);
        animation: blink 2s ease-in-out infinite;
    }

    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }

    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        background: #00ff41;
        border-radius: 50%;
        margin-right: 8px;
        box-shadow: 0 0 10px #00ff41;
        animation: statusBlink 1.5s ease-in-out infinite;
    }

    @keyframes statusBlink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
</style>

<div class="btc-container">
    <div class="matrix-bg" id="matrixBg"></div>
    <div class="btc-header">
        <h1 class="btc-title">⚡ BTCDETECT ⚡</h1>
        <div class="cyber-line"></div>
        <p class="btc-subtitle">
            <span class="status-indicator"></span>
            Scientific Methodology - OP_RETURN Protocol
        </p>
        <div class="warning-badge">⚠ DARKNET SECURE MODE ⚠</div>
    </div>
</div>

<script>
    // Matrix rain effect
    const matrixBg = document.getElementById('matrixBg');
    if (matrixBg) {
        const chars = '01アイウエオカキクケコサシスセソタチツテト';
        let matrix = '';
        for(let i = 0; i < 500; i++) {
            matrix += chars.charAt(Math.floor(Math.random() * chars.length));
            if(i % 50 === 0) matrix += '<br>';
        }
        matrixBg.innerHTML = matrix;
    }
</script>
""")

# ===================================================
# CYBERPUNK INPUT WIDGETS
# ===================================================

style = {
    'description_width': '180px'
}

layout = widgets.Layout(width='100%', height='40px')
text_layout = widgets.Layout(width='100%', height='80px')

input_style = """
<style>
    .widget-text input,
    .widget-textarea textarea {
        background: rgba(0, 0, 0, 0.8) !important;
        border: 2px solid #00ff41 !important;
        color: #00ff41 !important;
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 13px !important;
        padding: 10px !important;
        border-radius: 8px !important;
        box-shadow: inset 0 0 15px rgba(0, 255, 65, 0.2) !important;
        transition: all 0.3s ease !important;
    }

    .widget-text input:focus,
    .widget-textarea textarea:focus {
        border-color: #00ffff !important;
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.6),
                    inset 0 0 20px rgba(0, 255, 255, 0.2) !important;
        outline: none !important;
    }

    .widget-label {
        color: #00ff41 !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        letter-spacing: 1px !important;
        text-shadow: 0 0 5px rgba(0, 255, 65, 0.5) !important;
    }

    .widget-button {
        background: linear-gradient(135deg, #00ff41 0%, #00cc33 100%) !important;
        border: 2px solid #00ff41 !important;
        color: #000 !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 900 !important;
        font-size: 16px !important;
        padding: 12px 30px !important;
        border-radius: 10px !important;
        cursor: pointer !important;
        letter-spacing: 2px !important;
        box-shadow: 0 0 25px rgba(0, 255, 65, 0.6) !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
    }

    .widget-button:hover {
        background: linear-gradient(135deg, #00ffff 0%, #00cccc 100%) !important;
        border-color: #00ffff !important;
        box-shadow: 0 0 35px rgba(0, 255, 255, 0.8) !important;
        transform: scale(1.05) !important;
    }

    .widget-button:active {
        transform: scale(0.98) !important;
    }

    .widget-output {
        background: rgba(0, 0, 0, 0.9) !important;
        border: 2px solid #ff00ff !important;
        border-radius: 10px !important;
        padding: 20px !important;
        margin-top: 20px !important;
        box-shadow: 0 0 30px rgba(255, 0, 255, 0.4) !important;
        font-family: 'Share Tech Mono', monospace !important;
        color: #00ff41 !important;
    }
</style>
"""

display(HTML(input_style))

private_key_input = widgets.Text(
    description='🔑 Private Key (WIF):',
    placeholder='Enter your WIF private key...',
    style=style,
    layout=layout
)

utxo_txid_input = widgets.Text(
    description='🆔 UTXO TXID:',
    placeholder='Transaction ID (hex)...',
    style=style,
    layout=layout
)

utxo_index_input = widgets.IntText(
    description='📍 UTXO Index:',
    value=0,
    style=style,
    layout=layout
)

utxo_value_input = widgets.IntText(
    description='💰 UTXO Value (sat):',
    value=10000,
    style=style,
    layout=layout
)

recipient_input = widgets.Text(
    description='📬 Recipient Address:',
    placeholder='Bitcoin address...',
    style=style,
    layout=layout
)

send_amount_input = widgets.IntText(
    description='💸 Send Amount (sat):',
    value=5000,
    style=style,
    layout=layout
)

fee_input = widgets.IntText(
    description='⚡ Fee (sat):',
    value=1000,
    style=style,
    layout=layout
)

message_input = widgets.Textarea(
    description='📝 OP_RETURN Msg:',
    placeholder='Your message for OP_RETURN...',
    style=style,
    layout=text_layout
)

testnet_checkbox = widgets.Checkbox(
    value=True,
    description='🌐 Testnet Mode',
    style={'description_width': 'initial'}
)

create_button = widgets.Button(
    description='⚡ CREATE TRANSACTION ⚡',
    button_style='',
    layout=widgets.Layout(width='100%', height='50px')
)

output_area = widgets.Output()

# ===================================================
# CYBERPUNK OUTPUT FORMATTER
# ===================================================

def format_cyberpunk_output(btc_address, recipient, send_amount, fee, change, message, raw_tx):
    output_html = f"""
    <style>
        .cyber-output {{
            background: linear-gradient(135deg, #0a0a0a 0%, #1a0a1f 50%, #0a0a0a 100%);
            border: 2px solid #ff00ff;
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            box-shadow: 0 0 30px rgba(255, 0, 255, 0.5);
            font-family: 'Share Tech Mono', monospace;
            position: relative;
        }}

        .cyber-output::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #00ff41, #00ffff, #ff00ff, #00ff41);
            animation: scan 2s linear infinite;
        }}

        @keyframes scan {{
            0% {{ transform: translateX(-100%); }}
            100% {{ transform: translateX(100%); }}
        }}

        .output-title {{
            font-family: 'Orbitron', sans-serif;
            font-size: 24px;
            font-weight: 900;
            color: #ff00ff;
            text-align: center;
            margin-bottom: 20px;
            text-shadow: 0 0 20px rgba(255, 0, 255, 0.8);
            letter-spacing: 3px;
        }}

        .output-divider {{
            height: 2px;
            background: linear-gradient(90deg, transparent, #ff00ff, transparent);
            margin: 15px 0;
        }}

        .output-field {{
            margin: 12px 0;
            padding: 10px;
            background: rgba(0, 255, 65, 0.05);
            border-left: 3px solid #00ff41;
            border-radius: 5px;
        }}

        .field-label {{
            color: #00ffff;
            font-weight: bold;
            font-size: 13px;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }}

        .field-value {{
            color: #00ff41;
            font-size: 14px;
            word-break: break-all;
            margin-top: 5px;
        }}

        .success-badge {{
            display: inline-block;
            background: rgba(0, 255, 65, 0.2);
            border: 1px solid #00ff41;
            color: #00ff41;
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            margin: 15px 0;
            box-shadow: 0 0 15px rgba(0, 255, 65, 0.5);
        }}

        .broadcast-link {{
            display: block;
            text-align: center;
            margin-top: 20px;
            padding: 15px;
            background: rgba(0, 255, 255, 0.1);
            border: 2px solid #00ffff;
            border-radius: 10px;
            text-decoration: none;
            color: #00ffff;
            font-weight: bold;
            font-size: 14px;
            letter-spacing: 1px;
            transition: all 0.3s ease;
        }}

        .broadcast-link:hover {{
            background: rgba(0, 255, 255, 0.2);
            box-shadow: 0 0 25px rgba(0, 255, 255, 0.6);
            transform: scale(1.02);
        }}
    </style>

    <div class="cyber-output">
        <div class="output-title">⚡ BITCOIN TRANSACTION (OP_RETURN) ⚡</div>
        <div class="output-divider"></div>

        <div class="output-field">
            <div class="field-label">🔑 YOUR BTC ADDRESS:</div>
            <div class="field-value">{btc_address}</div>
        </div>

        <div class="output-field">
            <div class="field-label">📬 RECIPIENT ADDRESS:</div>
            <div class="field-value">{recipient}</div>
        </div>

        <div class="output-field">
            <div class="field-label">💸 SEND AMOUNT:</div>
            <div class="field-value">{send_amount} satoshi</div>
        </div>

        <div class="output-field">
            <div class="field-label">⚡ TRANSACTION FEE:</div>
            <div class="field-value">{fee} satoshi</div>
        </div>

        <div class="output-field">
            <div class="field-label">💰 CHANGE RETURNED:</div>
            <div class="field-value">{change} satoshi</div>
        </div>

        <div class="output-divider"></div>

        <div class="output-field">
            <div class="field-label">📝 OP_RETURN MESSAGE:</div>
            <div class="field-value">{message}</div>
        </div>

        <div class="output-divider"></div>

        <div class="output-field">
            <div class="field-label">🔐 RAWTX (HEX):</div>
            <div class="field-value">{raw_tx}</div>
        </div>

        <div style="text-align: center;">
            <div class="success-badge">✓ SAVED TO FILE: RawTX_OP_RETURN.txt</div>
        </div>

        <a href="https://cryptou.ru/btcdetect/transaction" target="_blank" class="broadcast-link">
            🚀 BLOCKCHAIN MESSAGE DECODER: https://cryptou.ru/btcdetect/transaction 🚀
        </a>
    </div>
    """
    return output_html

# ===================================================
# TRANSACTION CREATOR
# ===================================================

def on_create_button_clicked(b):
    with output_area:
        clear_output()

        try:
            private_key_wif = private_key_input.value.strip()
            utxo_txid = utxo_txid_input.value.strip()
            utxo_index = utxo_index_input.value
            utxo_value = utxo_value_input.value
            recipient_address = recipient_input.value.strip()
            send_amount = send_amount_input.value
            message = message_input.value.strip()
            fee = fee_input.value
            testnet = testnet_checkbox.value

            if not all([private_key_wif, utxo_txid, recipient_address, message]):
                display(HTML("""
                <div style="background: rgba(255, 0, 0, 0.2); border: 2px solid #ff0000; 
                     border-radius: 10px; padding: 20px; color: #ff0000; 
                     font-family: 'Share Tech Mono', monospace; text-align: center;
                     box-shadow: 0 0 20px rgba(255, 0, 0, 0.5);">
                    <strong>⚠ ERROR: All fields are required ⚠</strong>
                </div>
                """))
                return

            # Create transaction
            tx, change_amount = create_transaction_with_op_return(
                private_key_wif, utxo_txid, utxo_index, utxo_value,
                recipient_address, send_amount, message, fee, testnet
            )

            raw_tx = tx.serialize().hex()
            pk = PrivateKey.parse(private_key_wif)
            btc_address = pk.address()

            # Save to file
            with open("RawTX_OP_RETURN.txt", "w") as f:
                f.write(f"====================================\n")
                f.write(f"BITCOIN TRANSACTION (OP_RETURN)\n")
                f.write(f"====================================\n")
                f.write(f"Your BTC Address: {btc_address}\n")
                f.write(f"Recipient Address: {recipient_address}\n")
                f.write(f"Send Amount: {send_amount} satoshi\n")
                f.write(f"Transaction Fee: {fee} satoshi\n")
                f.write(f"Change Returned: {change_amount} satoshi\n\n")
                f.write(f"OP_RETURN Message: {message}\n\n")
                f.write(f"RawTX (Hex): {raw_tx}\n\n")
                f.write(f"✓ Saved to file: RawTX_OP_RETURN.txt\n\n")
                f.write(f"You can broadcast the transaction Using:\n")
                f.write(f"https://cryptou.ru/btcdetect/transaction\n")

            # Display cyberpunk output
            output_html = format_cyberpunk_output(
                btc_address, recipient_address, send_amount, 
                fee, change_amount, message, raw_tx
            )
            display(HTML(output_html))

        except Exception as e:
            display(HTML(f"""
            <div style="background: rgba(255, 0, 0, 0.2); border: 2px solid #ff0000; 
                 border-radius: 10px; padding: 20px; color: #ff0000; 
                 font-family: 'Share Tech Mono', monospace;
                 box-shadow: 0 0 20px rgba(255, 0, 0, 0.5);">
                <strong>⚠ ERROR:</strong><br>{str(e)}
            </div>
            """))

create_button.on_click(on_create_button_clicked)

# ===================================================
# DISPLAY INTERFACE
# ===================================================

display(header_html)
display(private_key_input)
display(utxo_txid_input)
display(utxo_index_input)
display(utxo_value_input)
display(recipient_input)
display(send_amount_input)
display(fee_input)
display(message_input)
display(testnet_checkbox)
display(create_button)
display(output_area)
