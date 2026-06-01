import json
import re

async def main(args: Args) -> Output:
    params = args.params
    input_raw = params.get('input', {})
    if isinstance(input_raw, str):
        input_data = json.loads(input_raw)
    else:
        input_data = input_raw

    juror_a = input_data.get('juror_a_output', '')
    juror_b = input_data.get('juror_b_output', '')
    juror_c = input_data.get('juror_c_output', '')

    ASR = input_data.get('ASR', '')
    Product_category = input_data.get('Product_category', '')
    item_id = input_data.get('item_id', '')
    aigc_video_id = input_data.get('aigc_video_id', '')

    def parse_result(output):
        if not output:
            return None, 0, ''
        result_match = re.search(r'最终结果[:：]\s*(\S.*?)\s*$', output, re.MULTILINE)
        result = result_match.group(1).strip() if result_match else None
        count_match = re.search(r'符合项数量[:：]\s*(\d+)/5', output)
        count = int(count_match.group(1)) if count_match else 0
        reason_match = re.search(r'判定理由[:：]\s*(\S.*?)\s*(?=\n\S+[:：]|\Z)', output, re.DOTALL)
        reason = reason_match.group(1).strip() if reason_match else ''
        return result, count, reason

    res_a, cnt_a, reason_a = parse_result(juror_a)
    res_b, cnt_b, reason_b = parse_result(juror_b)
    res_c, cnt_c, reason_c = parse_result(juror_c)

    votes = []
    for r in [res_a, res_b, res_c]:
        if r and ('✅' in r or 'OK' in r):
            votes.append('OK')
        elif r and ('❌' in r or 'not detailed' in r):
            votes.append('NOT_DETAILED')

    vote_ok = sum(1 for v in votes if v == 'OK')
    vote_not_detailed = sum(1 for v in votes if v == 'NOT_DETAILED')

    if vote_ok >= 2:
        final_result = '✅ OK'
    else:
        final_result = '❌ Description is not detailed'

    valid_counts = [c for c in [cnt_a, cnt_b, cnt_c] if c > 0]
    match_count_avg = round(sum(valid_counts) / len(valid_counts), 2) if valid_counts else 0

    reasons = []
    if reason_a:
        reasons.append(f'陪审员A: {reason_a}')
    if reason_b:
        reasons.append(f'陪审员B: {reason_b}')
    if reason_c:
        reasons.append(f'陪审员C: {reason_c}')
    reason_summary = ' | '.join(reasons)

    ret: Output = {
        'final_result': final_result,
        'vote_ok': vote_ok,
        'vote_not_detailed': vote_not_detailed,
        'juror_a_result': res_a or '解析失败',
        'juror_b_result': res_b or '解析失败',
        'juror_c_result': res_c or '解析失败',
        'match_count_avg': match_count_avg,
        'reason_summary': reason_summary,
        'ASR': ASR,
        'Product_category': Product_category,
        'item_id': item_id,
        'aigc_video_id': aigc_video_id
    }
    return ret
