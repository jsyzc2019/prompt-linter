import openai
import tiktoken
import re
import random
import configparser
import time
from io import StringIO
import sys
sys.path.insert(0, '.')


from pydt3 import DEVONthink3


stop_words_en = "-- ? “ ” 》 －－ able about above according accordingly across actually after afterwards again against ain't all allow allows almost alone along already also although always am among amongst an and another any anybody anyhow anyone anything anyway anyways anywhere apart appear appreciate appropriate are aren't around as a's aside ask asking associated at available away awfully be became because become becomes becoming been before beforehand behind being believe below beside besides best better between beyond both brief but by came can cannot cant can't cause causes certain certainly changes clearly c'mon co com come comes concerning consequently consider considering contain containing contains corresponding could couldn't course c's currently definitely described despite did didn't different do does doesn't doing done don't down downwards during each edu eg eight either else elsewhere enough entirely especially et etc even ever every everybody everyone everything everywhere ex exactly example except far few fifth first five followed following follows for former formerly forth four from further furthermore get gets getting given gives go goes going gone got gotten greetings had hadn't happens hardly has hasn't have haven't having he hello help hence her here hereafter hereby herein here's hereupon hers herself he's hi him himself his hither hopefully how howbeit however i'd ie if ignored i'll i'm immediate in inasmuch inc indeed indicate indicated indicates inner insofar instead into inward is isn't it it'd it'll its it's itself i've just keep keeps kept know known knows last lately later latter latterly least less lest let let's like liked likely little look looking looks ltd mainly many may maybe me mean meanwhile merely might more moreover most mostly much must my myself name namely nd near nearly necessary need needs neither never nevertheless new next nine no nobody non none noone nor normally not nothing novel now nowhere obviously of off often oh ok okay old on once one ones only onto or other others otherwise ought our ours ourselves out outside over overall own particular particularly per perhaps placed please plus possible presumably probably provides que quite qv rather rd re really reasonably regarding regardless regards relatively respectively right said same saw say saying says second secondly see seeing seem seemed seeming seems seen self selves sensible sent serious seriously seven several shall she should shouldn't since six so some somebody somehow someone something sometime sometimes somewhat somewhere soon sorry specified specify specifying still sub such sup sure take taken tell tends th than thank thanks thanx that thats that's the their theirs them themselves then thence there thereafter thereby therefore therein theres there's thereupon these they they'd they'll they're they've think third this thorough thoroughly those though three through throughout thru thus to together too took toward towards tried tries truly try trying t's twice two un under unfortunately unless unlikely until unto up upon us use used useful uses using usually value various very via viz vs want wants was wasn't way we we'd welcome well we'll went were we're weren't we've what whatever what's when whence whenever where whereafter whereas whereby wherein where's whereupon wherever whether which while whither who whoever whole whom who's whose why will willing wish with within without wonder won't would wouldn't yes yet you you'd you'll your you're yours yourself yourselves you've zero zt ZT zz ZZ"\
    .split(' ')
stop_words_cn = " 一 一下 一些 一切 一则 一天 一定 一方面 一旦 一时 一来 一样 一次 一片 一直 一致 一般 一起 一边 一面 万一 上下 上升 上去 上来 上述 上面 下列 下去 下来 下面 不一 不久 不仅 不会 不但 不光 不单 不变 不只 不可 不同 不够 不如 不得 不怕 不惟 不成 不拘 不敢 不断 不是 不比 不然 不特 不独 不管 不能 不要 不论 不足 不过 不问 与 与其 与否 与此同时 专门 且 两者 严格 严重 个 个人 个别 中小 中间 丰富 临 为 为主 为了 为什么 为什麽 为何 为着 主张 主要 举行 乃 乃至 么 之 之一 之前 之后 之後 之所以 之类 乌乎 乎 乘 也 也好 也是 也罢 了 了解 争取 于 于是 于是乎 云云 互相 产生 人们 人家 什么 什么样 什麽 今后 今天 今年 今後 仍然 从 从事 从而 他 他人 他们 他的 代替 以 以上 以下 以为 以便 以免 以前 以及 以后 以外 以後 以来 以至 以至于 以致 们 任 任何 任凭 任务 企图 伟大 似乎 似的 但 但是 何 何况 何处 何时 作为 你 你们 你的 使得 使用 例如 依 依照 依靠 促进 保持 俺 俺们 倘 倘使 倘或 倘然 倘若 假使 假如 假若 做到 像 允许 充分 先后 先後 先生 全部 全面 兮 共同 关于 其 其一 其中 其二 其他 其余 其它 其实 其次 具体 具体地说 具体说来 具有 再者 再说 冒 冲 决定 况且 准备 几 几乎 几时 凭 凭借 出去 出来 出现 分别 则 别 别的 别说 到 前后 前者 前进 前面 加之 加以 加入 加强 十分 即 即令 即使 即便 即或 即若 却不 原来 又 及 及其 及时 及至 双方 反之 反应 反映 反过来 反过来说 取得 受到 变成 另 另一方面 另外 只是 只有 只要 只限 叫 叫做 召开 叮咚 可 可以 可是 可能 可见 各 各个 各人 各位 各地 各种 各级 各自 合理 同 同一 同时 同样 后来 后面 向 向着 吓 吗 否则 吧 吧哒 吱 呀 呃 呕 呗 呜 呜呼 呢 周围 呵 呸 呼哧 咋 和 咚 咦 咱 咱们 咳 哇 哈 哈哈 哉 哎 哎呀 哎哟 哗 哟 哦 哩 哪 哪个 哪些 哪儿 哪天 哪年 哪怕 哪样 哪边 哪里 哼 哼唷 唉 啊 啐 啥 啦 啪达 喂 喏 喔唷 嗡嗡 嗬 嗯 嗳 嘎 嘎登 嘘 嘛 嘻 嘿 因 因为 因此 因而 固然 在 在下 地 坚决 坚持 基本 处理 复杂 多 多少 多数 多次 大力 大多数 大大 大家 大批 大约 大量 失去 她 她们 她的 好的 好象 如 如上所述 如下 如何 如其 如果 如此 如若 存在 宁 宁可 宁愿 宁肯 它 它们 它们的 它的 安全 完全 完成 实现 实际 宣布 容易 密切 对 对于 对应 将 少数 尔后 尚且 尤其 就 就是 就是说 尽 尽管 属于 岂但 左右 巨大 巩固 己 已经 帮助 常常 并 并不 并不是 并且 并没有 广大 广泛 应当 应用 应该 开外 开始 开展 引起 强烈 强调 归 当 当前 当时 当然 当着 形成 彻底 彼 彼此 往 往往 待 後来 後面 得 得出 得到 心里 必然 必要 必须 怎 怎么 怎么办 怎么样 怎样 怎麽 总之 总是 总的来看 总的来说 总的说来 总结 总而言之 恰恰相反 您 意思 愿意 慢说 成为 我 我们 我的 或 或是 或者 战斗 所 所以 所有 所谓 打 扩大 把 抑或 拿 按 按照 换句话说 换言之 据 掌握 接着 接著 故 故此 整个 方便 方面 旁人 无宁 无法 无论 既 既是 既然 时候 明显 明确 是 是否 是的 显然 显著 普通 普遍 更加 曾经 替 最后 最大 最好 最後 最近 最高 有 有些 有关 有利 有力 有所 有效 有时 有点 有的 有着 有著 望 朝 朝着 本 本着 来 来着 极了 构成 果然 果真 某 某个 某些 根据 根本 欢迎 正在 正如 正常 此 此外 此时 此间 毋宁 每 每个 每天 每年 每当 比 比如 比方 比较 毫不 没有 沿 沿着 注意 深入 清楚 满足 漫说 焉 然则 然后 然後 然而 照 照着 特别是 特殊 特点 现代 现在 甚么 甚而 甚至 用 由 由于 由此可见 的 的话 目前 直到 直接 相似 相信 相反 相同 相对 相对而言 相应 相当 相等 省得 看出 看到 看来 看看 看见 真是 真正 着 着呢 矣 知道 确定 离 积极 移动 突出 突然 立即 第 等 等等 管 紧接着 纵 纵令 纵使 纵然 练习 组成 经 经常 经过 结合 结果 给 绝对 继续 继而 维持 综上所述 罢了 考虑 者 而 而且 而况 而外 而已 而是 而言 联系 能 能否 能够 腾 自 自个儿 自从 自各儿 自家 自己 自身 至 至于 良好 若 若是 若非 范围 莫若 获得 虽 虽则 虽然 虽说 行为 行动 表明 表示 被 要 要不 要不是 要不然 要么 要是 要求 规定 觉得 认为 认真 认识 让 许多 论 设使 设若 该 说明 诸位 谁 谁知 赶 起 起来 起见 趁 趁着 越是 跟 转动 转变 转贴 较 较之 边 达到 迅速 过 过去 过来 运用 还是 还有 这 这个 这么 这么些 这么样 这么点儿 这些 这会儿 这儿 这就是说 这时 这样 这点 这种 这边 这里 这麽 进入 进步 进而 进行 连 连同 适应 适当 适用 逐步 逐渐 通常 通过 造成 遇到 遭到 避免 那 那个 那么 那么些 那么样 那些 那会儿 那儿 那时 那样 那边 那里 那麽 部分 鄙人 采取 里面 重大 重新 重要 鉴于 问题 防止 阿 附近 限制 除 除了 除此之外 除非 随 随着 随著 集中 需要 非但 非常 非徒 靠 顺 顺着 首先 高兴 是不是 说说  "\
    .split(' ')
stop_words_en = set(stop_words_en)
stop_words_cn = set(stop_words_cn)

dtp = DEVONthink3()
enc = tiktoken.get_encoding("cl100k_base")

CONFIG_FILENAME = '__chatgpt_config__'
TAG_GENERATION_PROMPT = "Generate < 10 tags from the summary, seperated by commas. The first two tags should be general, like Sports, Reading or Coding. Output the tags and nothingelse"

DEFAULT_CONFIG = {
    'GENERAL': {'api_key': ''},
    'ADD_TAGS': {'prompt': TAG_GENERATION_PROMPT, 'request_interval': 30}
}



def load_config():
    config = configparser.ConfigParser()
    config.read_dict(DEFAULT_CONFIG)
    result = dtp.search(f"name=={CONFIG_FILENAME}")
    if result:
        config.read_string(result[0].plain_text)
    else:
        save_config(config)
    return config

def save_config(config):
    output = StringIO()
    config.write(output)
    result = dtp.search(f"name=={CONFIG_FILENAME}")
    if result:
        record = result[0]
        record.plain_text = output.getvalue()
    else:
        record = dtp.create_record_with({
            "name": CONFIG_FILENAME,
            "type": "txt",
            "plain text": output.getvalue()
        })
    return record
config = load_config()
def get_api_key():
    if config.get('GENERAL', 'api_key'):
        api_key = config.get('GENERAL', 'api_key')
    else:
        response = dtp.display_dialog("Please enter your OpenAI API key", "")
        api_key = response["textReturned"]
        config['GENERAL']['api_key'] = api_key
        save_config(config)
    
    return api_key

def token_counts(content) -> int:
    return len(enc.encode(content))

def truncate_content(content) -> list[str]:
    for stop_cn in stop_words_cn:
        content = content.replace(stop_cn, '')
    for stop_en in stop_words_en:
        content = re.sub(r'\b{}\b'.format(re.escape(stop_en)), '', content)
    
    tokens = enc.encode(content)
    max_length = 3800
    first = 1500
    last = 1000
    middle = max_length - first - last
    if token_counts(content) <= max_length:
        return content
    


    first_tokens = tokens[:first]
    last_tokens = tokens[-last:]
    middle_tokens = random.choices(tokens[first:-last], k=middle)


    content = enc.decode(first_tokens + middle_tokens + last_tokens)
    return content

def generate_tags(content) -> list[str]:
    content = truncate_content(content)
    print(content)
    prompt = """Please analyze the following text and provide < 10 tags separated by commas. Output only the tags and nothing else.  If there are any errors, starts with "!!!"""
    additional = "The tags should reflect the major topics."
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt},
            {"role": "user", "content": additional},
            {"role": "user", "content": "content: " + content}
        ]
    )
    response = completion.choices[0]['message']['content']
    if response.startswith("!!!"):
        raise ValueError(response.replace("!!!", ""))
    return [tag.strip() for tag in response.split(",")]

def chat_once(messages: list) -> str:
    error_prompt = 'If something is wrong, reply starts with "!!!"'
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": error_prompt}
        ] + [{"role": "user", "content": message} for message in messages]
    )
    response = completion.choices[0]['message']['content']
    if response.strip().startswith("!!!"):
        raise ValueError(response.replace("!!!", ""))
    return response

def generate_tags_v2(content) -> list[str]:
    content = truncate_content(content)
    print(content)
    
    summarize_prompt = """Summerize the following text:"""
    summary = chat_once([summarize_prompt, content])
    print("summary: ", summary)
    time.sleep(5)
    tags = chat_once([config.get('ADD_TAGS', 'prompt'), summary])
    print("tags: ", tags)
    return [tag.strip() for tag in tags.split(",")]



def add_tags_to_selected_records():
    openai.api_key = get_api_key()
    records = dtp.selected_records
    has_error = False
    error_message = "Error occurs when handling following records:\n"
    total = len(records)
    dtp.show_progress_indicator("Generating tags...", cancel_button=True, steps=total)

    first = True
    for record in records:
        try:
            if not first:
                time.sleep(config.getint('ADD_TAGS', 'request_interval'))
            dtp.step_progress_indicator("Generating tags for " + record.name)
            tags = generate_tags_v2('title: ' + record.name + '\ncontent: ' + record.plain_text)
            record.tags = tags
        except Exception as e:
            has_error = True
            error_message += f"\n{record.name}\n==========\n {e}\n"
            break
            
        
    
    if has_error:
        dtp.display_dialog(error_message)
        dtp.hide_progress_indicator()
    
if __name__ == '__main__':
    add_tags_to_selected_records()