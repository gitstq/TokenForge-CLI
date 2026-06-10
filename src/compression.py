"""
Compression strategies module - 6 intelligent compression strategies for LLM token optimization.
"""

import re
import math
from typing import Dict, List, Optional, Tuple
from .token_estimator import TokenEstimator


class CompressionStrategy:
    """Base class for compression strategies."""

    name: str = "base"
    description: str = ""
    category: str = "general"

    def compress(self, text: str, intensity: float = 0.5) -> Tuple[str, Dict]:
        """Compress text and return (compressed_text, stats)."""
        raise NotImplementedError

    def _build_stats(self, original: str, compressed: str, details: Dict = None) -> Dict:
        """Build compression statistics."""
        token_stats = TokenEstimator.compression_ratio(original, compressed)
        stats = {
            "strategy": self.name,
            "original_chars": len(original),
            "compressed_chars": len(compressed),
            "saved_chars": len(original) - len(compressed),
            "saved_percent": round((1 - len(compressed) / len(original)) * 100, 1) if original else 0,
            "token_ratio": token_stats["ratio"],
            "token_saved_percent": token_stats["saved_percent"],
        }
        if details:
            stats.update(details)
        return stats


class KeywordExtractionStrategy(CompressionStrategy):
    """Extract key sentences and phrases, removing filler content."""

    name = "keyword_extraction"
    description = "Extract key sentences and phrases, remove filler content"
    category = "semantic"

    # Common filler patterns in English
    EN_FILLER_PATTERNS = [
        r"\b(in order to)\b",
        r"\b(for the purpose of)\b",
        r"\b(it is important to note that)\b",
        r"\b(it should be noted that)\b",
        r"\b(as a matter of fact)\b",
        r"\b(in the context of)\b",
        r"\b(with regard to)\b",
        r"\b(in terms of)\b",
        r"\b(on the other hand)\b",
        r"\b(at the end of the day)\b",
        r"\b(to be honest)\b",
        r"\b(to tell you the truth)\b",
        r"\b(as far as I( am|'m) concerned)\b",
        r"\b(in my opinion)\b",
        r"\b(from my perspective)\b",
        r"\b(it goes without saying)\b",
        r"\b(last but not least)\b",
        r"\b(first and foremost)\b",
        r"\b(in addition to that)\b",
        r"\b(needless to say)\b",
    ]

    # Common filler patterns in Chinese
    ZH_FILLER_PATTERNS = [
        r"(?:众所周知|大家都知道|不言而喻|毫无疑问|毋庸置疑)",
        r"(?:事实上|实际上|其实|本质上|从根本上说)",
        r"(?:值得注意|需要指出|必须强调|应该看到)",
        r"(?:从某种意义上|在某种程度上|从一定角度)",
        r"(?:总的来说|总而言之|综上所述|概而言之)",
        r"(?:换句话说|换言之|也就是说|即)",
        r"(?:首先.*?其次.*?(?:最后|最终))",
        r"(?:不可否认|无可厚非|毋庸置疑)",
    ]

    def compress(self, text: str, intensity: float = 0.5) -> Tuple[str, Dict]:
        if not text:
            return text, self._build_stats(text, text)

        compressed = text
        removed_count = 0

        # Apply English filler removal
        for pattern in self.EN_FILLER_PATTERNS:
            matches = re.findall(pattern, compressed, re.IGNORECASE)
            compressed = re.sub(pattern, "", compressed, flags=re.IGNORECASE)
            removed_count += len(matches)

        # Apply Chinese filler removal
        for pattern in self.ZH_FILLER_PATTERNS:
            matches = re.findall(pattern, compressed)
            compressed = re.sub(pattern, "", compressed)
            removed_count += len(matches)

        # Remove excessive whitespace
        compressed = re.sub(r"  +", " ", compressed)
        compressed = re.sub(r"\n{3,}", "\n\n", compressed)
        compressed = compressed.strip()

        # Score-based sentence filtering for higher intensity
        if intensity > 0.6:
            sentences = re.split(r'(?<=[.!?。！？\n])', compressed)
            sentences = [s.strip() for s in sentences if s.strip()]

            if len(sentences) > 3:
                scored = []
                for sent in sentences:
                    score = self._sentence_importance(sent)
                    scored.append((sent, score))

                # Keep top sentences based on intensity
                keep_ratio = 1.0 - (intensity - 0.6) * 0.5  # 0.7 -> keep 80%, 1.0 -> keep 65%
                keep_count = max(3, int(len(scored) * keep_ratio))
                scored.sort(key=lambda x: x[1], reverse=True)

                # Keep order but filter low-importance
                threshold = sorted([s[1] for s in scored], reverse=True)[min(keep_count - 1, len(scored) - 1)]
                kept = [s[0] for s in scored if s[1] >= threshold]
                compressed = " ".join(kept)

        stats = self._build_stats(text, compressed, {
            "filler_removed": removed_count,
            "strategy_detail": "keyword_extraction",
        })
        return compressed, stats

    def _sentence_importance(self, sentence: str) -> float:
        """Score sentence importance based on information density."""
        score = 0.0

        # Length factor (prefer medium-length sentences)
        words = len(sentence.split())
        if 5 <= words <= 30:
            score += 2.0
        elif 3 <= words <= 50:
            score += 1.0

        # Contains numbers (likely specific information)
        if re.search(r"\d+", sentence):
            score += 1.5

        # Contains proper nouns or technical terms (capitalized words)
        if re.search(r"\b[A-Z][a-z]{2,}\b", sentence):
            score += 1.0

        # Contains key indicators
        key_indicators = [
            "result", "conclusion", "finding", "key", "important",
            "critical", "significant", "main", "core", "essential",
            "结果", "结论", "发现", "关键", "重要", "核心", "主要",
        ]
        for indicator in key_indicators:
            if indicator.lower() in sentence.lower():
                score += 1.0
                break

        # Penalize very short sentences
        if words < 3:
            score -= 1.0

        return max(0, score)


class SemanticDedupStrategy(CompressionStrategy):
    """Remove semantically duplicate or near-duplicate content."""

    name = "semantic_dedup"
    description = "Remove semantically duplicate or near-duplicate content"
    category = "semantic"

    def compress(self, text: str, intensity: float = 0.5) -> Tuple[str, Dict]:
        if not text:
            return text, self._build_stats(text, text)

        lines = text.split("\n")
        unique_lines = []
        removed_count = 0
        similarity_threshold = 0.7 - (intensity * 0.2)  # Higher intensity = lower threshold

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if unique_lines and unique_lines[-1].strip() != "":
                    unique_lines.append(line)
                continue

            is_duplicate = False
            for existing in unique_lines:
                sim = self._text_similarity(stripped, existing.strip())
                if sim > similarity_threshold:
                    is_duplicate = True
                    removed_count += 1
                    break

            if not is_duplicate:
                unique_lines.append(line)

        compressed = "\n".join(unique_lines)
        compressed = re.sub(r"\n{3,}", "\n\n", compressed)

        stats = self._build_stats(text, compressed, {
            "duplicates_removed": removed_count,
            "similarity_threshold": round(similarity_threshold, 2),
        })
        return compressed, stats

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity using character n-grams."""
        if not text1 or not text2:
            return 0.0

        # Quick length-based check
        len_ratio = min(len(text1), len(text2)) / max(len(text1), len(text2))
        if len_ratio < 0.3:
            return 0.0

        # Character trigram similarity
        def get_trigrams(text):
            text = text.lower()
            return set(text[i:i+3] for i in range(len(text) - 2))

        t1_trigrams = get_trigrams(text1)
        t2_trigrams = get_trigrams(text2)

        if not t1_trigrams or not t2_trigrams:
            return 0.0

        intersection = t1_trigrams & t2_trigrams
        union = t1_trigrams | t2_trigrams

        return len(intersection) / len(union) if union else 0.0


class StructuredCompressionStrategy(CompressionStrategy):
    """Compress structured content (JSON, code blocks, lists) efficiently."""

    name = "structured"
    description = "Compress structured content (JSON, code, lists) efficiently"
    category = "structural"

    def compress(self, text: str, intensity: float = 0.5) -> Tuple[str, Dict]:
        if not text:
            return text, self._build_stats(text, text)

        compressed = text
        operations = []

        # Compress code blocks - remove comments
        if intensity > 0.3:
            def remove_code_comments(match):
                code = match.group(1)
                # Remove single-line comments
                code = re.sub(r"#[^\n]*", "", code)  # Python/Shell
                code = re.sub(r"//[^\n]*", "", code)  # JS/C/Java
                # Remove multi-line comments
                code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
                code = re.sub(r'"""[\s\S]*?"""', "", code)  # Python docstrings
                code = re.sub(r"'''[\s\S]*?'''", "", code)
                operations.append("code_comments_removed")
                first_line = match.group(0).split('\n')[0]
                return "```" + first_line + "\n" + code.strip() + "\n```"

            compressed = re.sub(r"```(\w*)\n([\s\S]*?)```", remove_code_comments, compressed)

        # Compress numbered lists - use ranges
        if intensity > 0.5:
            def compress_numbered_list(match):
                items = match.group(0).split("\n")
                if len(items) > 5:
                    operations.append("list_compacted")
                    return "\n".join(items[:3]) + f"\n  ... ({len(items) - 3} more items)\n" + items[-1]
                return match.group(0)

            compressed = re.sub(
                r"(?:^\d+[.)]\s+.+\n){5,}",
                compress_numbered_list,
                compressed,
                flags=re.MULTILINE
            )

        # Compress repeated whitespace in structured content
        compressed = re.sub(r"[ \t]{2,}", " ", compressed)

        # Remove empty lines between structured blocks
        compressed = re.sub(r"\n{2,}(?=\S)", "\n", compressed)

        stats = self._build_stats(text, compressed, {
            "operations": operations,
        })
        return compressed, stats


class TemplateCompressionStrategy(CompressionStrategy):
    """Replace verbose patterns with compact templates/shorthand."""

    name = "template"
    description = "Replace verbose patterns with compact templates"
    category = "structural"

    # Template replacements: (pattern, replacement)
    TEMPLATES = [
        # English abbreviations
        (r"\b(artificial intelligence)\b", "AI"),
        (r"\b(machine learning)\b", "ML"),
        (r"\b(deep learning)\b", "DL"),
        (r"\b(natural language processing)\b", "NLP"),
        (r"\b(large language model)\b", "LLM"),
        (r"\b(reinforcement learning)\b", "RL"),
        (r"\b(computer vision)\b", "CV"),
        (r"\b(application programming interface)\b", "API"),
        (r"\b(graphical user interface)\b", "GUI"),
        (r"\b(command line interface)\b", "CLI"),
        (r"\b(integrated development environment)\b", "IDE"),
        (r"\b(object-oriented programming)\b", "OOP"),
        (r"\b(software development kit)\b", "SDK"),
        (r"\b(operating system)\b", "OS"),
        (r"\b(database management system)\b", "DBMS"),
        (r"\b(content delivery network)\b", "CDN"),
        (r"\b(return on investment)\b", "ROI"),
        (r"\b(key performance indicator)\b", "KPI"),
        (r"\b(frequently asked questions)\b", "FAQ"),
        (r"\b(for example|for instance)\b", "e.g."),
        (r"\b(that is|in other words)\b", "i.e."),
        (r"\b(et cetera)\b", "etc."),
        (r"\b(versus)\b", "vs"),
        (r"\b(maximum)\b", "max"),
        (r"\b(minimum)\b", "min"),
        (r"\b(average)\b", "avg"),
        (r"\b(standard)\b", "std"),
        (r"\b(configuration)\b", "config"),
        (r"\b(information)\b", "info"),
        (r"\b(documentation)\b", "docs"),
        (r"\b(application)\b", "app"),
        (r"\b(implementation)\b", "impl"),
        (r"\b(specification)\b", "spec"),
        (r"\b(environment)\b", "env"),
        (r"\b(authentication)\b", "auth"),
        (r"\b(authorization)\b", "authz"),
        (r"\b(directory)\b", "dir"),
        (r"\b(regular expression)\b", "regex"),
        (r"\b(assembly)\b", "asm"),
        (r"\b(binary)\b", "bin"),
        (r"\b(temporary)\b", "temp"),
        (r"\b(reference)\b", "ref"),
        (r"\b(different)\b", "diff"),
        (r"\b(function)\b", "fn"),
        (r"\b(parameter)\b", "param"),
        (r"\b(argument)\b", "arg"),
        (r"\b(execute|execution)\b", "exec"),
        (r"\b(initialize|initialization)\b", "init"),
        (r"\b(serialize|serialization)\b", "ser"),
        (r"\b(deserialize|deserialization)\b", "deser"),
        (r"\b(allocate|allocation)\b", "alloc"),
        (r"\b(deallocate|deallocation)\b", "dealloc"),
        (r"\b(buffer)\b", "buf"),
        (r"\b(pointer)\b", "ptr"),
        (r"\b(array)\b", "arr"),
        (r"\b(string)\b", "str"),
        (r"\b(boolean)\b", "bool"),
        (r"\b(integer)\b", "int"),
        (r"\b(character)\b", "char"),
        (r"\b(number)\b", "num"),
        (r"\b(object)\b", "obj"),
        (r"\b(value)\b", "val"),
        (r"\b(error)\b", "err"),
        (r"\b(exception)\b", "exc"),
        (r"\b(message)\b", "msg"),
        (r"\b(package)\b", "pkg"),
        (r"\b(module)\b", "mod"),
        (r"\b(component)\b", "comp"),
        (r"\b(service)\b", "svc"),
        (r"\b(version)\b", "ver"),
        (r"\b(representation)\b", "repr"),
        (r"\b(architecture)\b", "arch"),
        (r"\b(infrastructure)\b", "infra"),
        (r"\b(deployment)\b", "deploy"),
        (r"\b(production)\b", "prod"),
        (r"\b(development)\b", "dev"),
        (r"\b(staging)\b", "stg"),
        (r"\b(testing)\b", "test"),
        (r"\b(repository)\b", "repo"),
        (r"\b(through)\b", "thru"),
        (r"\b(between)\b", "btwn"),
        (r"\b(because)\b", "cuz"),
        (r"\b(although|though)\b", "altho"),
        (r"\b(probably)\b", "prob"),
        (r"\b(especially)\b", "esp"),
        (r"\b(necessary)\b", "nec"),
        (r"\b(previous|previously)\b", "prev"),
        (r"\b(additional)\b", "add'l"),
        (r"\b(optional)\b", "opt"),
        (r"\b(required)\b", "req'd"),
        (r"\b(available)\b", "avail"),
        (r"\b(individual)\b", "indiv"),
        (r"\b(specific|specifically)\b", "spec"),
        (r"\b(general|generally)\b", "gen"),
        (r"\b(particular|particularly)\b", "partic"),
        (r"\b(similar|similarly)\b", "sim"),
        (r"\b(various)\b", "var"),
        (r"\b(approximately)\b", "~"),
        (r"\b(regarding)\b", "re:"),
        (r"\b(following)\b", "per"),
        (r"\b(regardless of)\b", "w/o"),
        (r"\b(without)\b", "w/o"),
        (r"\b(within)\b", "w/in"),
        (r"\b(as soon as possible)\b", "ASAP"),
        (r"\b(for what it's worth)\b", "FWIW"),
        (r"\b(in my humble opinion)\b", "IMHO"),
        (r"\b(by the way)\b", "BTW"),
        (r"\b(right now)\b", "RN"),
        # Chinese abbreviations
        (r"(?:人工智能)", "AI"),
        (r"(?:机器学习)", "ML"),
        (r"(?:深度学习)", "DL"),
        (r"(?:自然语言处理)", "NLP"),
        (r"(?:大语言模型|大型语言模型)", "LLM"),
        (r"(?:强化学习)", "RL"),
        (r"(?:计算机视觉)", "CV"),
        (r"(?:应用程序|应用软件)", "App"),
        (r"(?:操作系统)", "OS"),
        (r"(?:数据库)", "DB"),
        (r"(?:用户界面)", "UI"),
        (r"(?:应用程序接口|应用编程接口)", "API"),
        (r"(?:命令行界面)", "CLI"),
        (r"(?:集成开发环境)", "IDE"),
        (r"(?:面向对象编程)", "OOP"),
        (r"(?:软件开发工具包)", "SDK"),
        (r"(?:内容分发网络)", "CDN"),
        (r"(?:投资回报率)", "ROI"),
        (r"(?:关键绩效指标)", "KPI"),
        (r"(?:常见问题)", "FAQ"),
        (r"(?:例如|比如)", "e.g."),
        (r"(?:也就是说|换言之)", "i.e."),
        (r"(?:等等|诸如此类)", "etc."),
        (r"(?:以及)", "&"),
        (r"(?:或者)", "|"),
        (r"(?:信息)", "info"),
        (r"(?:文档|文档资料)", "docs"),
        (r"(?:配置|配置文件)", "config"),
        (r"(?:环境|运行环境)", "env"),
        (r"(?:认证|身份认证)", "auth"),
        (r"(?:授权)", "authz"),
        (r"(?:目录|文件夹)", "dir"),
        (r"(?:函数)", "fn"),
        (r"(?:参数)", "param"),
        (r"(?:执行|运行)", "exec"),
        (r"(?:初始化)", "init"),
        (r"(?:版本)", "ver"),
        (r"(?:架构|体系结构)", "arch"),
        (r"(?:基础设施)", "infra"),
        (r"(?:部署|上线)", "deploy"),
        (r"(?:生产|正式环境)", "prod"),
        (r"(?:开发)", "dev"),
        (r"(?:测试)", "test"),
        (r"(?:仓库|代码库)", "repo"),
        (r"(?:特别是|尤其是)", "esp"),
        (r"(?:必要|必须的)", "nec"),
        (r"(?:之前|先前)", "prev"),
        (r"(?:可选的)", "opt"),
        (r"(?:必需的|必须的)", "req'd"),
        (r"(?:可用|可获取)", "avail"),
        (r"(?:具体|具体来说)", "spec"),
        (r"(?:一般|通常)", "gen"),
        (r"(?:类似|相似)", "sim"),
        (r"(?:各种|多种)", "var"),
        (r"(?:关于|至于)", "re:"),
        (r"(?:尽快)", "ASAP"),
    ]

    def compress(self, text: str, intensity: float = 0.5) -> Tuple[str, Dict]:
        if not text:
            return text, self._build_stats(text, text)

        compressed = text
        replacements = 0

        # Apply template replacements based on intensity
        apply_count = int(len(self.TEMPLATES) * (0.3 + intensity * 0.7))

        for pattern, replacement in self.TEMPLATES[:apply_count]:
            new_text = re.sub(pattern, replacement, compressed, flags=re.IGNORECASE)
            if new_text != compressed:
                replacements += len(re.findall(pattern, compressed, flags=re.IGNORECASE))
                compressed = new_text

        # Compress verbose number expressions
        compressed = re.sub(r"\b(one)\b", "1", compressed, flags=re.IGNORECASE)
        compressed = re.sub(r"\b(two)\b", "2", compressed, flags=re.IGNORECASE)
        compressed = re.sub(r"\b(three)\b", "3", compressed, flags=re.IGNORECASE)
        compressed = re.sub(r"\b(four)\b", "4", compressed, flags=re.IGNORECASE)
        compressed = re.sub(r"\b(five)\b", "5", compressed, flags=re.IGNORECASE)

        # Clean up extra spaces
        compressed = re.sub(r"  +", " ", compressed)

        stats = self._build_stats(text, compressed, {
            "replacements": replacements,
            "templates_applied": apply_count,
        })
        return compressed, stats


class ChunkOptimizationStrategy(CompressionStrategy):
    """Optimize text chunking for LLM context windows."""

    name = "chunk_optimization"
    description = "Optimize text chunking for LLM context windows"
    category = "structural"

    def __init__(self, max_chunk_tokens: int = 2000):
        self.max_chunk_tokens = max_chunk_tokens

    def compress(self, text: str, intensity: float = 0.5) -> Tuple[str, Dict]:
        if not text:
            return text, self._build_stats(text, text)

        # Split into paragraphs
        paragraphs = re.split(r"\n\s*\n", text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        if len(paragraphs) <= 1:
            return text, self._build_stats(text, text, {"chunks": 1})

        # Score and rank paragraphs
        scored_paragraphs = []
        for i, para in enumerate(paragraphs):
            score = self._paragraph_score(para, i, len(paragraphs))
            scored_paragraphs.append((para, score, i))

        # Calculate target token budget
        total_tokens = TokenEstimator.estimate(text)
        target_tokens = int(total_tokens * (1.0 - intensity * 0.4))  # 40-60% reduction

        # Select paragraphs within budget
        scored_paragraphs.sort(key=lambda x: x[1], reverse=True)
        selected = []
        current_tokens = 0

        for para, score, orig_idx in scored_paragraphs:
            para_tokens = TokenEstimator.estimate(para)
            if current_tokens + para_tokens <= target_tokens:
                selected.append((para, orig_idx))
                current_tokens += para_tokens
            elif current_tokens == 0:
                # Always include at least the highest-scored paragraph
                selected.append((para, orig_idx))
                current_tokens = para_tokens

        # Restore original order
        selected.sort(key=lambda x: x[1])
        compressed = "\n\n".join(p[0] for p in selected)

        stats = self._build_stats(text, compressed, {
            "original_paragraphs": len(paragraphs),
            "selected_paragraphs": len(selected),
            "target_tokens": target_tokens,
            "actual_tokens": current_tokens,
        })
        return compressed, stats

    def _paragraph_score(self, paragraph: str, index: int, total: int) -> float:
        """Score paragraph importance for selection."""
        score = 0.0

        # Information density
        tokens = TokenEstimator.estimate(paragraph)
        chars = len(paragraph)
        if chars > 0:
            density = tokens / chars
            score += density * 10

        # Contains specific data
        if re.search(r"\d+", paragraph):
            score += 2.0

        # Contains technical terms
        if re.search(r"[A-Z]{2,}", paragraph):
            score += 1.5

        # Position bonus (beginning and end are usually more important)
        if index < 2:
            score += 1.0
        if index >= total - 2:
            score += 0.5

        # Length penalty for very short paragraphs
        if len(paragraph.split()) < 5:
            score -= 0.5

        return max(0, score)


class ChineseOptimizationStrategy(CompressionStrategy):
    """Specialized compression for Chinese text - remove redundancy and optimize encoding."""

    name = "chinese_optimization"
    description = "Specialized compression for Chinese text redundancy removal"
    category = "language_specific"

    # Chinese redundant patterns
    ZH_REDUNDANT_PATTERNS = [
        (r"(?:的)(?:的)", "的"),  # Double 的
        (r"(?:了)(?:了)", "了"),  # Double 了
        (r"(?:是)(?:是)", "是"),  # Double 是
        (r"(?:在)(?:在)", "在"),  # Double 在
        (r"(?:了)(?:一下)", "一下"),
        (r"(?:进行)(?:一下)(?:分析|研究|讨论|调查|测试|检查)", lambda m: m.group(0)[2:]),
        (r"(?:对.*?进行)(?:一下)?(?:分析|研究|讨论|调查|测试|检查)", lambda m: m.group(0)[1:].replace("进行", "").replace("一下", "")),
        (r"(?:通过)(?:使用|利用|采用)(.*?)(?:来|去|实现|完成)", r"\1"),
        (r"(?:使用)(?:了)?(?:一下)?", ""),
        (r"(?:利用)(?:了)?(?:一下)?", ""),
        (r"(?:采用)(?:了)?(?:一下)?", ""),
        (r"(?:根据)(?:相关|有关|对应)", "根据"),
        (r"(?:相关)(?:的)?(?:信息|数据|内容|资料|文件)", "相关信息"),
        (r"(?:各种)(?:各样的|类型的|形式的)", "各类"),
        (r"(?:大量)(?:的|个|种|项)", "大量"),
        (r"(?:一定)(?:的|个|种|程度)", "一定"),
        (r"(?:不同)(?:的|个|种|类型)", "不同"),
        (r"(?:相同)(?:的|个|种|类型)", "相同"),
        (r"(?:目前|当前|现在|此时)(?:来说|来看|而言|情况下)", "当前"),
        (r"(?:随着)(?:.*?)(?:的)(?:发展|进步|变化|提升)", ""),
        (r"(?:在)(?:此|这)(?:基础|前提|条件|背景)(?:上|下)", ""),
        (r"(?:从)(?:整体|宏观|全局|总体)(?:来看|而言|角度)", ""),
        (r"(?:以)(?:上|下|前|后)(?:的|了)", ""),
        (r"(?:可以)(?:被|得到|进行|加以)", ""),
        (r"(?:需要)(?:被|得到|进行|加以)", "需"),
        (r"(?:能够)(?:被|得到|进行|加以)", "能"),
        (r"(?:已经)(?:被|得到|完成|实现)", "已"),
        (r"(?:将会)(?:被|得到|完成|实现)", "将"),
        (r"(?:正在)(?:被|得到|进行)", "正"),
    ]

    def compress(self, text: str, intensity: float = 0.5) -> Tuple[str, Dict]:
        if not text:
            return text, self._build_stats(text, text)

        compressed = text
        operations = {}

        # Check if text contains Chinese
        has_chinese = bool(re.search(r"[\u4e00-\u9fff]", text))
        if not has_chinese:
            return text, self._build_stats(text, text, {"chinese_content": False})

        # Apply Chinese-specific optimizations
        apply_count = int(len(self.ZH_REDUNDANT_PATTERNS) * (0.3 + intensity * 0.7))

        for pattern, replacement in self.ZH_REDUNDANT_PATTERNS[:apply_count]:
            if callable(replacement):
                matches = re.findall(pattern, compressed)
                if matches:
                    compressed = re.sub(pattern, replacement, compressed)
                    operations[pattern[:20]] = len(matches)
            else:
                matches = re.findall(pattern, compressed)
                if matches:
                    compressed = re.sub(pattern, replacement, compressed)
                    operations[pattern[:20]] = len(matches)

        # Remove excessive punctuation
        compressed = re.sub(r"([。！？])\1+", r"\1", compressed)
        compressed = re.sub(r"(，)\1+", "，", compressed)
        compressed = re.sub(r"(、)\1+", "、", compressed)

        # Compose consecutive short sentences
        if intensity > 0.6:
            compressed = re.sub(r"([。！？])\s*\n", r"\1", compressed)

        # Clean up
        compressed = re.sub(r"  +", "", compressed)
        compressed = re.sub(r"\n{3,}", "\n\n", compressed)
        compressed = compressed.strip()

        stats = self._build_stats(text, compressed, {
            "chinese_content": True,
            "operations_count": sum(operations.values()),
            "patterns_applied": apply_count,
        })
        return compressed, stats


class CompressionEngine:
    """Main compression engine that orchestrates all strategies."""

    STRATEGIES = {
        "keyword_extraction": KeywordExtractionStrategy,
        "semantic_dedup": SemanticDedupStrategy,
        "structured": StructuredCompressionStrategy,
        "template": TemplateCompressionStrategy,
        "chunk_optimization": ChunkOptimizationStrategy,
        "chinese_optimization": ChineseOptimizationStrategy,
    }

    def __init__(self):
        self._strategies = {name: cls() for name, cls in self.STRATEGIES.items()}

    def get_strategy(self, name: str) -> CompressionStrategy:
        """Get a compression strategy by name."""
        if name not in self._strategies:
            available = ", ".join(self._strategies.keys())
            raise ValueError(f"Unknown strategy: {name}. Available: {available}")
        return self._strategies[name]

    def list_strategies(self) -> List[Dict]:
        """List all available compression strategies."""
        return [
            {
                "name": name,
                "description": strategy.description,
                "category": strategy.category,
            }
            for name, strategy in self._strategies.items()
        ]

    def compress(self, text: str, strategies: List[str] = None,
                  intensity: float = 0.5) -> Tuple[str, Dict]:
        """Compress text using specified strategies (or all if None)."""
        if not text:
            return text, {"error": "Empty text"}

        if strategies is None:
            strategies = list(self.STRATEGIES.keys())

        current_text = text
        all_stats = []
        pipeline = []

        for strategy_name in strategies:
            strategy = self.get_strategy(strategy_name)
            compressed, stats = strategy.compress(current_text, intensity)
            pipeline.append({
                "strategy": strategy_name,
                "input_chars": len(current_text),
                "output_chars": len(compressed),
                "saved_chars": len(current_text) - len(compressed),
            })
            all_stats.append(stats)
            current_text = compressed

        # Final statistics
        token_stats = TokenEstimator.compression_ratio(text, current_text)

        result = {
            "original_text": text,
            "compressed_text": current_text,
            "strategies_used": strategies,
            "intensity": intensity,
            "pipeline": pipeline,
            "original_chars": len(text),
            "compressed_chars": len(current_text),
            "char_saved_percent": round((1 - len(current_text) / len(text)) * 100, 1) if text else 0,
            "original_tokens": token_stats["original_tokens"],
            "compressed_tokens": token_stats["compressed_tokens"],
            "token_saved_percent": token_stats["saved_percent"],
            "token_ratio": token_stats["ratio"],
            "strategy_stats": all_stats,
        }

        return current_text, result

    def compress_file(self, file_path: str, strategies: List[str] = None,
                      intensity: float = 0.5) -> Tuple[str, Dict]:
        """Read file and compress its content."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return self.compress(content, strategies, intensity)
        except FileNotFoundError:
            return "", {"error": f"File not found: {file_path}"}
        except Exception as e:
            return "", {"error": str(e)}
