![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.001.png)

**TradingAgents: Multi-Agents LLM Financial Trading Framework**

**Yijia Xiao** 1,3**, Edward Sun** 1,3**, Di Luo** 1,2**, Wei Wang** 1,3

1University of California, Los Angeles (UCLA) 2Massachusetts Institute of Technology (MIT) 3Tauric Research[*](#_page0_x82.47_y702.39)

**Significant progress has been made in automated problem-solving using societies of agents pow- ered by large language models (LLMs). In finance, efforts have largely focused on single-agent systems handling specific tasks or multi-agent frameworks independently gathering data. However, the multi-agent systems’ potential to replicate real-world trading firms’ collaborative dynamics remains underexplored.** TradingAgents **proposes a novel stock trading framework inspired by trading firms, featuring LLM-powered agents in specialized roles such as fundamental analysts, sentiment analysts, technical analysts, and traders with varied risk profiles. The framework in- cludes Bull and Bear researcher agents assessing market conditions, a risk management team monitoring exposure, and traders synthesizing insights from debates and historical data to make informed decisions. By simulating a dynamic, collaborative trading environment, this framework aims to improve trading performance. Detailed architecture and extensive experiments reveal its superiority over baseline models, with notable improvements in cumulative returns, Sharpe ratio, and maximum drawdown, highlighting the potential of multi-agent LLM frameworks in financial trading. T RADING AGENTS is available at[ https://github.com/TauricResearch/TradingAgents**.**](https://github.com/TauricResearch/TradingAgents)**

1. **Introduction**

Autonomous agents leveraging Large Language Models (LLMs) present a transformative approach to decision-making by replicating human processes and workflows across various applications. These systems enhance the problem-solving capabilities of language agents by equipping them with tools and enabling collaboration with other agents, effectively breaking down complex problems into manageable components [(Havrilla et al., 2024;](#_page13_x42.33_y478.52)[ Park et al., 2023;](#_page15_x42.33_y136.76)[ Talebirad and Nadiri, 2023;](#_page15_x42.33_y258.50)[ Tang et al., 2024](#_page15_x42.33_y294.56)). One prominent application of these autonomous frameworks is in the financial market—a highly complex system influenced by numerous factors, including company fundamentals, market sentiment, technical indicators, and macroeconomic events.

Traditional algorithmic trading systems often rely on quantitative models that struggle to fully cap- ture the complex interplay of diverse factors. In contrast, LLMs excel at processing and understanding natural language data, making them particularly effective for tasks that require textual comprehension, such as analyzing news articles, financial reports, and social media sentiment. Additionally, deep learning-based trading systems often suffer from low explainability, as they rely on hidden features that drive decision-making but are difficult to interpret. Recent advancements in multi-agent LLM frameworks for finance have shown significant promise in addressing these challenges. These frame- works create explainable AI systems, where decisions are supported by evidence and transparent![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.002.png)

\*T<a name="_page0_x82.47_y702.39"></a>auric Research Organization: https://tauric.ai

TradingAgents: Multi-Agents LLM Financial Trading Framework![ref1]

reasoning [(Li et al., 2023a;](#_page14_x42.33_y87.14)[ Wang et al., 2024c;](#_page15_x42.33_y610.38)[ Yu et al., 2024](#_page16_x42.33_y470.50)), demonstrating the potential in financial applications.

Despite their potential, most current applications of language agents in the financial and trading sectors face two significant limitations:

**Lack of Realistic Organizational Modeling:** Many frameworks fail to capture the complex interactions between agents that mimic the structure of real-world trading firms [(Li et al., 2023a; ](#_page14_x42.33_y87.14)[Wang et al., 2024c;](#_page15_x42.33_y610.38)[ Yu et al., 2024](#_page16_x42.33_y470.50)). Instead, they focus narrowly on specific task performance, often disconnected from the organizational workflows and established human operating procedures proven effective in trading. This limits their ability to fully replicate and benefit from real-world trading practices.

**Inefficient Communication Interfaces:** Most existing systems use natural language as the primary communication medium, typically relying on message histories or an unstructured pool of information for decision-making [(Park et al., 2023;](#_page15_x42.33_y136.76)[ Qian et al., 2024](#_page15_x42.33_y172.82)). This approach often results in a “telephone effect”, where details are lost, and states become corrupted as conversations lengthen. Agents struggle to maintain context and track extended histories while filtering out irrelevant information from previous decision steps, diminishing their effectiveness in handling complex, dynamic tasks. Additionally, the unstructured pool-of-information approach lacks clear instructions, forcing logical communication and information exchange between agents to depend solely on retrieval, which disrupts the relational integrity of the data.

In this work, we address these key limitations of existing models by introducing a system that overcomes these challenges. First, our framework bridges the gap by simulating the multi-agent decision-making processes typical of professional trading teams. It incorporates specialized agents tailored to distinct aspects of trading, inspired by the organizational structure of real-world trading firms. These agents include fundamental analysts, sentiment/news analysts, technical analysts, and traders with diverse risk profiles. Bullish and bearish debaters evaluate market conditions to provide balanced recommendations, while a risk management team ensures that exposures remain within acceptable limits. Second, to enhance communication, our framework combines structured outputs for control, clarity, and reasoning with natural language dialogue to facilitate effective debate and collaboration among agents. This hybrid approach ensures both precision and flexibility in decision-making.

We validate our framework through experiments on historical financial data, comparing its performance against multiple baselines. Comprehensive evaluation metrics, including cumulative return, Sharpe ratio, and maximum drawdown, are employed to assess its overall effectiveness.

2. **Related Work**
1. **LLMs as Financial Assistants**

Large Language Models (LLMs) are applied in finance by fine-tuning on financial data or training on financial corpora. This improves the model’s understanding of financial terminology and data, enabling a specialized assistant for analytical support, insights, and information retrieval, rather than trade execution.

**Fine-Tuned LLMs for Finance**

Fine-tuning enhances domain-specific performance. Examples include PIXIU (FinMA) [(Xie et al., 2023](#_page16_x42.33_y87.14)), which fine-tuned LLaMA on 136K finance-related instructions; FinGPT [(Touvron et al., 2023; ](#_page15_x42.33_y344.18)[Yang et al., 2023b](#_page16_x42.33_y263.08)), which used LoRA to fine-tune models like LLaMA and ChatGLM with about 50K

finance-specific samples; and Instruct-FinGPT [(Zhang et al., 2023a](#_page16_x42.33_y520.12)), fine-tuned on 10K instruction samples from financial sentiment analysis datasets. These models outperform their base versions and other open-source LLMs like BLOOM and OPT [(Zhang et al., 2022)](#_page16_x42.33_y605.80) in finance classification tasks, even surpassing BloombergGPT [(Wu et al., 2023)](#_page15_x42.33_y646.44) in several evaluations. However, in generative tasks, they perform similarly or slightly worse than powerful general-purpose models like GPT-4, indicating a need for more high-quality, domain-specific datasets.

**Finance LLMs Trained from Scratch**

Training LLMs from scratch on finance-specific corpora aims for better domain adaptation. Models like BloombergGPT [(Wu et al., 2023](#_page15_x42.33_y646.44)), XuanYuan 2.0 [(Zhang et al., 2023b](#_page17_x42.33_y87.14)), and Fin-T5 [(Lu et al., 2023)](#_page14_x42.33_y221.69) combine public datasets with finance-specific data during pretraining. BloombergGPT, for instance, was trained on both general and financial text, with proprietary Bloomberg data enhancing its performance on finance benchmarks. These models outperform general-purpose counterparts like BLOOM-176B and T5 in tasks such as market sentiment classification and summarization. While they may not match larger closed-source models like GPT-3 or PaLM [(Chowdhery et al., 2022](#_page13_x42.33_y189.80)), they offer competitive performance among similar-sized open-source models without compromising general language understanding.

In summary, finance-specific LLMs developed through fine-tuning or training from scratch show significant improvements in domain-specific tasks, underscoring the importance of domain adaptation and the potential for further enhancements with high-quality finance-specific datasets.

![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.004.png)

**Fig. 1**: **TradingAgents** Overall Framework Organization. **I. ANALYSTS TEAM**: Four analysts concurrently gather relevant market information. **II. RESEARCH TEAM**: The team discusses and evaluates the collected data. **III. TRADER**: Based on the researchers’ analysis, the trader makes the trading decision. **IV. RISK MANAGEMENT TEAM**: Risk guardians assess the decision against current market conditions to mitigate risks.

**V. FUND MANAGER**: The fund manager approves and executes the trade.

2. **LLMs as Traders**

LLMs act as trader agents making direct trading decisions by analyzing external data like news, financial reports, and stock prices. Proposed architectures include news-driven, reasoning-driven, and reinforcement learning (RL)-driven agents.

**News-Driven Agents**

News-driven architectures integrate stock news and macroeconomic updates into LLM prompts to predict stock price movements. Studies evaluating both closed-source models (e.g., GPT-3.5, GPT-

\4) and open-source LLMs (e\.g\., Qwen [(Bai et al., 2023](#_page13_x42.33_y113.09)), Baichuan [(Yang et al., 2023a](#_page16_x42.33_y172.82))) in financial

sentiment analysis have shown the effectiveness of simple long-short strategies based on sentiment scores [(Lopez-Lira and Tang, 2023](#_page14_x42.33_y185.88)). Further research on fine-tuned LLMs like FinGPT and OPT demonstrates improved performance through domain-specific alignment [(Kirtac and Germano, 2024; ](#_page13_x42.33_y613.81)[Zhang et al., 2024a](#_page16_x42.33_y556.18)). Advanced methods involve summarizing news data and reasoning about their relationship with stock prices [(Fatouros et al., 2024a;](#_page13_x42.33_y406.39)[ Wang et al., 2024b](#_page15_x42.33_y524.70)).

**Reasoning-Driven Agents**

Reasoning-driven agents enhance trading decisions through mechanisms like reflection and debate. Reflection-driven agents, such as FinMem [(Yu et al., 2023)](#_page16_x42.33_y420.89) and FinAgent [(Zhang et al., 2024b](#_page16_x42.33_y668.96)), use layered memorization and multimodal data to summarize inputs into memories, inform decisions, and incorporate technical indicators, achieving superior backtest performance while mitigating hallu- cinations [(Ji et al., 2023](#_page13_x42.33_y577.74)). Debate-driven agents, like those in heterogeneous frameworks [(Xing, 2024) ](#_page16_x42.33_y136.76)and TradingGPT [(Li et al., 2023b](#_page14_x42.33_y136.51)), enhance reasoning and factual validity by employing LLM debates among agents with different roles, improving sentiment classification and increasing robustness in trading decisions.

**Reinforcement Learning-Driven Agents**

Reinforcement learning methods align LLM outputs with expected behaviors, using backtesting as rewards. SEP [(Koa et al., 2024)](#_page13_x42.33_y663.42) employs RL with memorization and reflection to refine LLM predictions based on market history. Classical RL methods are also used in trading frameworks that integrate LLM-generated embeddings with stock features, trained via algorithms like Proximal Policy Optimization (PPO) [(Ding et al., 2023;](#_page13_x42.33_y320.71)[ Schulman et al., 2017](#_page15_x42.33_y222.43)).

3. **LLMs as Alpha Miners**

LLMs are also used to generate alpha factors instead of making direct trading decisions. QuantAgent [(Wang et al., 2023)](#_page15_x42.33_y560.77) demonstrates this by leveraging LLMs to produce alpha factors through an inner- loop and outer-loop architecture. In the inner loop, a writer agent generates a script from a trader’s idea, while a judge agent provides feedback. In the outer loop, the code is tested in the real market, and trading results enhance the judge agent. This approach enables progressive approximation of optimal behavior.

Subsequent research, such as AlphaGPT [(Wang et al., 2023](#_page15_x42.33_y560.77)), proposes a human-in-the-loop frame- work for alpha mining with a similar architecture. Both studies showcase the effectiveness of LLM- powered alpha mining systems, highlighting their potential in automating and accelerating the development of trading strategies by generating and refining alpha factors.

3. **TradingAgents: Role Specialization**

Assigning LLM agents clear, well-defined roles with specific goals enables the breakdown of complex objectives into smaller, manageable subtasks. Financial trading is a prime example of such complexity, demanding the integration of diverse signals, inputs, and specialized expertise. In the real world, this approach to managing complexity is demonstrated by trading firms that rely on expert teams to collaborate and make high-stakes decisions, underscoring the multifaceted nature of the task.

In a typical trading firm, vast amounts of data are collected, including financial metrics, price movements, trading volumes, historical performance, economic indicators, and news sentiment. This data is then analyzed by quantitative experts (quants), including mathematicians, data scientists, and engineers, using advanced tools and algorithms to identify trends and predict market movements.

Inspired by this organizational structure, TradingAgents defines seven distinct agent roles within a simulated trading firm: Fundamentals Analyst, Sentiment Analyst, News Analyst, Technical Analyst, Researcher, Trader, and Risk Manager. Each agent is assigned a specific name, role, goal, and set of constraints, alongside predefined context, skills, and tools tailored to their function. For example, a Sentiment Analyst is equipped with tools like web search engines, Reddit search APIs, X/Twitter search tools, and sentiment score calculation algorithms, while a Technical Analyst can execute code, calculate technical indicators, and analyze trading patterns. More specifically, TradingAgents assumes the following teams.

1. **Analyst Team**

The Analyst Team (Figure[` `**2**)](#_page4_x66.33_y280.70) is composed of specialized agents responsible for gathering and analyzing various types of market data to inform trading decisions. Each agent focuses on a specific aspect of market analysis, bringing together a comprehensive view of the market’s conditions.

5
TradingAgents: Multi-Agents LLM Financial Trading Framework![ref1]

Goal:![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.005.png)

Analyze market trends using Market technical indicators

Key Points Summary: 

Tech Sector Growth

RSI: Strong fluctuations, overbought conditions, price corrections expected ... (ADX, Bollinger Bands...)

Goal:![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.006.png)

Analyze global economic News trends affecting markets

Key Points Summary: 

Global Econ Trends & Sector Insights

US Economic Policy: Trump’s return sparks mixed reactions... (AI & Tech Growth, Semiconductor Focus ...)

Goal:

Analyze social media ![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.007.png)MSoecdiaial  sentiment trends

Key Points Summary: 

AAPL Social Sentiment (Nov 4-19, 2024)

Positive Sentiment Peaks: Notable on Nov 15 (0.5445) and Nov 11 (0.426)... (Negative Sentiment,  High Engagement...)

Goal:![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.008.png)

Analyze&evaluate company mFuenndtaals- financials &stock performance

Key Points Summary: 

Apple Inc . Financial Anal ysis

Strong Pro fitability: High margins, impressive  ROE and  ROA ... (Liquidity&Leverage Risks,  Valuation  Concerns...)


TradingAgents: Multi-Agents LLM Financial Trading Framework![ref1]

<a name="_page4_x66.33_y280.70"></a>**Fig. 2**: TradingAgents Analyst Team

- **Fundamental Analyst Agents**: These agents evaluate company fundamentals by analyzing financial statements, earnings reports, insider transactions, and other pertinent data. They assess a company’s intrinsic value to identify undervalued or overvalued stocks, providing insights into long-term investment potential.
- **Sentiment Analyst Agents**: These agents process large volumes of social media posts, sentiment scores, and insider sentiments derived from public information and social media activity. They gauge market sentiment to predict how collective investor behavior might impact stock prices in the short term.
- **News Analyst Agents**: These agents analyze news articles, government announcements, and other macroeconomic indicators to assess the market’s macroeconomic state, major world events, and significant company changes. They identify news events that could influence market movements, helping to anticipate sudden shifts in market dynamics.
- **Technical Analyst Agents**: These agents calculate and select relevant technical indicators, such as Moving Average Convergence Divergence (MACD) and Relative Strength Index (RSI), cus- tomized for specific assets. They analyze price patterns and trading volumes to forecast future price movements, assisting in timing entry and exit points.

Collectively, the Analyst Team synthesizes data from multiple sources to provide a holistic market analysis. Their combined insights form the foundational input for the Researcher Team, ensuring that all facets of the market are considered in subsequent decision-making processes.

2. **Researcher Team**

The Researcher Team (Figure[` `**3**)](#_page5_x66.33_y331.14) is responsible for critically evaluating the information provided by the Analyst Team. Comprised of agents adopting both bullish and bearish perspectives, they engage in multiple rounds of debate to assess the potential risks and benefits of investment decisions.

Goal: Goal:![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.009.png)![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.010.png)

Evaluate the investment  Assess the risks of investing Bullish potential of Apple Inc. Bearish in Apple Inc.

Key Points Summary:  Debate Key Points Summary: ![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.011.png)

Apple Investment Outlook Apple Investment Risks

Growth Potential: AI-powered smart home expansion  Competitive Challenges: Late entry into smart home drives revenue... (Strong Financials, Market  market, ... (Geopolitical Tensions, 

Sentiment...) Valuation&Liquidity...)

<a name="_page5_x66.33_y331.14"></a>**Fig. 3**: TradingAgents Researcher Team: Bullish Perspectives and Bearish Perspectives

- **Bullish Researchers**: These agents advocate for investment opportunities by highlighting posi- tive indicators, growth potential, and favorable market conditions. They construct arguments supporting the initiation or continuation of positions in certain assets.
- **Bearish Researchers**: Conversely, these agents focus on potential downsides, risks, and unfavor- able market signals. They provide cautionary insights, questioning the viability of investment strategies and highlighting possible negative outcomes.

Through this dialectical process, the Researcher Team aims to reach a balanced understanding of the market situation. Their thorough analysis helps in identifying the most promising investment strategies while anticipating possible challenges, thus aiding the Trader Agents in making informed decisions.

3. **Trader Agents**

Trader Agents (Figure[` `**4**)](#_page6_x66.33_y121.47) are responsible for executing trading decisions based on the comprehensive analysis provided by the Analyst Team and the nuanced perspectives from the Researcher Team. They assess the synthesized information, considering both quantitative data and qualitative insights, to determine optimal trading actions.

![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.012.png)

<a name="_page6_x66.33_y121.47"></a>**Fig. 4**: TradingAgents’s Trader Decision-Making Process The tasks of TradingAgents Trader include:

- Evaluating recommendations and insights from analysts and researchers.
- Deciding on the timing and size of trades to maximize trading returns.
- Placing buy or sell orders in the market.
- Adjusting portfolio allocations in response to market changes and new information.

Trader Agents must balance potential returns against associated risks, making timely decisions in a dynamic market environment. Their actions directly impact the firm’s performance, necessitating a high level of precision and strategic thinking.

4. **Risk Management Team**

The Risk Management Team (Figure[` `**5**)](#_page7_x66.33_y82.96) monitors and controls the firm’s exposure to various market risks. These agents continuously evaluate the portfolio’s risk profile, ensuring that trading activities remain within predefined risk parameters and comply with regulatory requirements.

The responsibilities of Risk Management Team include:

- Assessing factors such as market volatility, liquidity, and counterparty risks.
- Implementing risk mitigation strategies, such as setting stop-loss orders or diversifying holdings.
- Providing feedback to Trader Agents on risk exposures and suggesting adjustments to trading strategies.
- Ensuring that the overall portfolio aligns with the firm’s risk tolerance and investment objectives.

By offering oversight and guidance, the Risk Management Team helps maintain the firm’s financial stability and protect against adverse market events. They play a crucial role in safeguarding assets and ensuring sustainable long-term performance.

All agents in TradingAgents follow the ReAct prompting framework [(Yao et al., 2023](#_page16_x42.33_y384.82)), which synergizes reasoning and acting. The environment state is shared and monitored by the agents, enabling them to take context-appropriate actions such as conducting research, executing trades, engaging in debates, or managing risks. This design ensures a collaborative, dynamic decision-making process reflective of real-world trading systems.

Goal: Goal:![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.013.png)![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.014.png)

Advocate for high-reward, high-risk  Provide investment recommendations Risky investment strategies Manager based on market analysis![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.015.png)

Goal: Report

Provide a balanced perspective on  Key Points Summary: 

Neutral Apple investment

Buy Recommendation for Apple

Goal:

Strong Fundamentals: Robust earnings growth and Emphasize a conservative investment  market capitalization ... (Innovation Leadership, 

Safe strategy with risk mitigation Resilience to Risks...)

<a name="_page7_x66.33_y82.96"></a>**Fig. 5**: TradingAgents Risk Management Team and Fund Manager Approval Workflow

4. **TradingAgents: Agent Workflow**
1. **Communication Protocol**

Most existing LLM-based agent frameworks use natural language as the primary communication interface, typically through structured message histories or collections of agent-generated messages [(Fatouros et al., 2024b;](#_page13_x42.33_y442.45)[ Li et al., 2023a;](#_page14_x42.33_y87.14)[ Yang et al., 2023c,](#_page16_x42.33_y299.15)[ 2024](#_page16_x42.33_y335.21)). However, relying solely on natu- ral language often proves insufficient for solving complex, long-term tasks that require extensive planning horizons. In such cases, pure natural language communication can resemble a game of telephone—over multiple iterations, initial information may be forgotten or distorted due to context length limitations and an overload of text that obscures critical earlier details [(Hong et al., 2024](#_page13_x42.33_y528.13)). To address this limitation, we draw inspiration from frameworks like MetaGPT, which adopt a structured approach to communication. Our model introduces a structured communication protocol to govern agent interactions. By clearly defining each agent’s state, we ensure that each role only extracts or queries the necessary information, processes it, and returns a completed report. This streamlined approach reduces unnecessary steps, lowers the risk of message corruption, and keeps interactions focused and efficient, even in complex, long-horizon tasks.

2. **Types of Agent Interactions**

In contrast to previous multi-agent trading frameworks, which rely heavily on natural language dialogue, TradingAgents agents communicate primarily through structured documents and diagrams. These documents encapsulate the agents’ insights in concise, well-organized reports that preserve essential content while avoiding irrelevant information. By utilizing structured reports, agents can query necessary details directly from the global state, eliminating the need for lengthy conversations that risk diluting information, extending the message state indefinitely, and causing data loss. The types of documents and the information they contain are detailed below:

1. **Analyst Team**: Fundamental, sentiment, news, and technical analysts compile their research and

findings into concise analysis reports specific to their areas of expertise. These reports include key metrics, insights, and recommendations based on their specialized analyses.

2. **Traders**: Traders review and analyze the reports from the analysts, carefully deliberating to

produce clear decision signals. They accompany these decisions with detailed reports explaining their rationale and supporting evidence, which are later utilized by the risk management team.

Agents engage in natural language dialogue exclusively during agent-to-agent conversations

and debates. These concise, focused discussions have been shown to promote deeper reasoning and integrate diverse perspectives, enabling more balanced decisions in complex, long-horizon scenarios—a method particularly relevant to the intricate environment of trading [(Du et al., 2023](#_page13_x42.33_y370.32)). This approach seamlessly integrates with our structured framework, as the conversation state is recorded as a structured entry within the overall agent state. The types of communication in these scenarios are detailed below:

3. **Researcher Team**: Each researcher agent queries the global agent state for analyst reports

and carefully forms their opinion. Two researchers represent opposing perspectives: one bullish and one bearish. They engage in natural language dialogue for n rounds, as determined by the debate facilitator agent. At the conclusion, the facilitator reviews the debate history, selects the prevailing perspective, and records it as a structured entry in the communication protocol.

4. **Risk Management Team**: The risk management team, similar to the researcher team, queries

the trader’s decision and accompanying report. They then deliberate from three perspectives—risk- seeking, neutral, and risk-conservative—to adjust the trading plan within risk constraints. They engage in n rounds of natural language discussion, guided by a facilitator agent.

5. **Fund manager**: The fund manager reviews the discussion from the risk management team,

determines the appropriate risk adjustments, and updates the trader’s decision and report states within the communication protocol.

3. **Backbone LLMs**

To meet the diverse complexity and speed demands of tasks in our framework, we strategically select Large Language Models (LLMs) based on their strengths. Quick-thinking models, such as gpt-4o-mini and gpt-4o, efficiently handle fast, low-depth tasks like summarization, data retrieval, and converting tabular data to text [(OpenAI et al., 2024](#_page14_x42.33_y306.88)). In contrast, deep-thinking models like o1-preview excel in reasoning-intensive tasks such as decision-making, evidence-based report writing, and data analysis. These models leverage their architectures for multi-round reasoning, producing logically sound, in-depth insights [(OpenAI, 2024;](#_page14_x42.33_y271.06)[ Wang et al., 2024a;](#_page15_x42.33_y475.09)[ Zhong et al., 2024](#_page17_x42.33_y123.21)). Additionally, we prioritize models with proven reliability and scalability to ensure optimal performance across variousmarketconditions. Wealsoemployauxiliaryexpertmodelsforspecializedtaskslikesentiment analysis.

Specifically, all analyst nodes rely on deep-thinking models to ensure robust analysis, while quick- thinking models handle data retrieval from APIs and tools for efficiency. Researchers and traders use deep-thinking models to generate valuable insights and support well-informed decisions. By aligning the choice of LLMs with the specific requirements of each task, our framework achieves a balance between efficiency and depth of reasoning, which is crucial for effective trading strategies.

This implementation strategy ensures that TradingAgents can be deployed without requiring a GPU, relying only on API credits. It also introduces seamless exchangeability of backbone models, enabling researchers to effortlessly replace the model with any locally hosted or API-accessible alternatives in the future. This adaptability supports the integration of improved reasoning models or finance-tuned models customized for specific tasks. As a result, TradingAgents is highly scalable and future-proof, offering flexibility to accommodate any backbone model for any of its agents.

5. **Experiments**
1. **Simulation Setup**

We evaluate our TradingAgents framework using a comprehensive backtesting simulation from January 1st to March 29th, 2024, across major technology stocks including Apple, Nvidia, Microsoft, Meta, and Google. TradingAgents facilitates seamless plug-and-play strategies during the simulation, enabling straightforward comparisons with any baseline. Agents make decisions based solely on data available up to each trading day, ensuring no future data is used (eliminating look-ahead bias). Based on their analysis, TradingAgents generates trading signals to buy, sell, or hold assets, which are then executed. Afterward, analysis metrics are calculated before proceeding to the next day’s data.

We benchmark against five established strategies: Buy and Hold, MACD, KDJ+RSI, ZMR, and SMA (baseline descriptions in Appendix[ S1.1](#_page18_x66.33_y118.47)). Performance is evaluated using four key metrics: Cumulative Return (CR), Annualized Return (AR), Sharpe Ratio (SR), and Maximum Drawdown (MDD) (formulations in Appendix[ S1.2](#_page18_x66.33_y340.39)).

2. **Back Trading**

To simulate a realistic trading environment, we utilize a multi-asset and multi-modal financial dataset comprising of various stocks such as Apple, Nvidia, Microsoft, Meta, Google, and more. Our multi- modal dataset integrates historical stock prices, news articles, social media sentiment, insider transac- tions, financial statements, and 60 technical indicators per asset. The dataset includes:

**Historical Stock Prices**: Open, high, low, close, volume, and adjusted close prices from January 1st, 2024, to March 29th, 2024.

**News Articles**: Daily news updates are gathered from diverse sources such as Bloomberg, Yahoo, EODHD, FinnHub, and Reddit, covering specific company developments, global events, macroeco- nomic trends, and government updates.

**Social Media Posts and Sentiment**: Posts from Reddit, X/Twitter, and other platforms along with sentiment scores of posts calculated by auxiliary language models.

**Insider Sentiments and Transactions**: Sentiment derived from public information, including transactions from SEDI and relevant company filings.

**Financial Statements and Earnings Reports**: Quarterly and annual reports filed by companies.

**Company Profiles and Financial History**: Descriptions of company profiles, target industries, and financial history reported by third parties.

**Technical Indicators**: Sixty standard technical analysis indicators calculated for each asset, includ- ing MACD, RSI, Bollinger Bands, etc.

6. **Results and Analysis**

In this section, we present the experimental results and analyze the performance of TradingAgents in comparison to the baseline models.



|Broker (None) cash 246516.57|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
| - | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- |
|value 130501.44||||||||246516\.57|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|<p>Trades - Net Profit/Loss (True) Positive</p><p>Negative</p>|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|AAPL\_data (1 Day) O:171.13 H:171.61 L:169.9|0 C:170.86||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|<p>Volume</p><p>BuySell (True, 0.015)</p>|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|<p>buy</p><p>sell 174.18</p>|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||174\.18|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||170\.86|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
150M 125M 100M 75M 50M 25M 0M

<a name="_page10_x66.33_y82.96"></a>**Fig. 6**: **TradingAgents** Detailed Transaction History for $AAPL. Green **/** Red Arrows indicate Long **/** Short Positions respectively, showing the model’s trading decisions over time.

1. **Performance Comparison**
1. **Cumulative and Annual Returns**

Table[` `**1** ](#_page10_x66.33_y582.20)and Figures[` `**6**,](#_page10_x66.33_y82.96)[` `**7**,](#_page11_x66.33_y82.96)[ S1,](#_page19_x66.33_y390.94)[ S2,](#_page20_x66.33_y103.59)[ S3,](#_page20_x66.33_y443.70) and[ S4 ](#_page21_x66.33_y82.96)demonstrate that our method outperforms existing rule-based trading baselines, particularly in profitability, as measured by returns. TradingAgents achieves at least a 23.21% cumulative return and a 24.90% annual return on the three sampled stocks, surpassing the best-performing baselines by a margin of 6.1%. Notably, on $AAPL stock—a particularly challenging case due to market volatility during the testing period—traditional methods struggled, as their patterns failed to generalize to this situation. In contrast, TradingAgents excelled under these adverse conditions, achieving returns exceeding 26% within months.

**Table 1**: Performance comparison across all methods using four evaluation metrics. Results highlighted in **green** represent the best-performing statistic for each model. The improvement row illustrates TradingAgents’s performance gains over the top-performing baselines.![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.016.png)

<a name="_page10_x66.33_y582.20"></a>AAPL GOOGL AMZN

Categories Models CR%↑ ARR%↑ SR↑ MDD%↓ CR%↑ ARR%↑ SR↑ MDD%↓ CR%↑ ARR%↑ SR↑ MDD%↓



|Market B&H|-5.23|-5.09|-1.29|11\.90|7\.78|8\.09|1\.35|13\.04|17\.1|17\.6|3\.53|3\.80|
| - | - | - | - | - | - | - | - | - | - | - | - | - |
|<p>MACD Rule-based KDJ&RSI</p><p>ZMR</p><p>SMA</p>|-1.49 2.05 0.57 -3.2|-1.48 2.07 0.57 -2.97|-0.81 1.64 0.17 -1.72|4\.53 1.09 **0.86** 3.67|6\.20 0.4 -0.58 6.23|6\.26 0.4 0.58 6.43|2\.31 0.02 2.12 2.12|**1.22** 1.58 2.34 2.34|- -0.77 -0.77 11.01|- -0.76 -0.77 11.6|- -2.25 -2.45 2.22|- 1.08 **0.82** 3.97|
|Ours TradingAgents|**26.62**|**30.5**|**8.21**|0\.91|**24.36**|**27.58**|**6.39**|1\.69|**23.21**|**24.90**|**5.60**|2\.11|
|Improvement(%)|24\.57|28\.43|6\.57|-|16\.58|19\.49|4\.26|-|6\.10|7\.30|2\.07|-|

Strategy Comparison - Cumulative Returns for AAPL![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.017.png)

||<p>Strategies BuyAndHoldStrategy MACDStrategy KDJRSIStrategy ZMRStrategy SMAStrategy </p><p>**TradingAgents**</p>||||||
| :- | :- | :- | :- | :- | :- | :- |
||||||||
||||||||
||||||||
||||||||
||||||||
||||||||
||||||||
1\.30 1.25 1.20 1.15 1.10 1.05 1.00 0.95

2024-01-01 2024-01-15 2024-02-01 2024-02-15 2024-03-01 2024-03-15 2024-04-01

Date

<a name="_page11_x66.33_y82.96"></a>**Fig. 7**: Cumulative Returns on $AAPL using **TradingAgents**. The figure shows the performance comparison of our model against baseline approaches for Apple Inc. stock analysis.

2. **Sharpe Ratio**

The Sharpe Ratio[† ](#_page11_x82.47_y632.13)performance highlights TradingAgents’s exceptional ability to deliver superior risk- adjustedreturns, surpassingallbaselinemodels. ThisresultunderscoresTradingAgents’seffectiveness in balancing returns and risk— a crucial factor for sustainable and predictable investment growth. TradingAgents outperforms market benchmarks such as Buy-and-Hold and rule-based strategies consistently, demonstrating its adaptability. Its capability to maximize returns while maintaining controlled risk exposure establishes a strong foundation for multi-agent and debate-based automated trading algorithms.

3. **Maximum Drawdown**

While rule-based baselines demonstrated superior performance in controlling risk, as reflected by their maximum drawdown scores, they fell short in capturing high returns. This trade-off between risk and reward underscores TradingAgents’s strength as a balanced approach. Despite higher returns being typically associated with higher risks, TradingAgents maintained a relatively low maximum drawdown compared to many baselines. Its effective risk-control mechanisms, facilitated by the debates among risk-control agents, ensured that the maximum drawdown remained within a

†W<a name="_page11_x82.47_y632.13"></a>e benchmarked TradingAgents over 3 months due to intensive LLM and tool use (11 LLM calls & 20+ tool calls/pre- ![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.018.png)diction). The highest Sharpe Ratio exceeds our expected empirical range (SR above 2 – very good, above 3 – excellent). We exported TradingAgents’s decision sequences and examined them to ensure calculation correctness. We believe the exceptionally high SR resulted from the phenomenon that there were few pullbacks in TradingAgents during that period. We report results as they are in our experiments faithfully. Future work will optimize LLM reasoning & tool use to enable longer backtesting under limited budgets.

manageable limit, not exceeding 2. This demonstrates TradingAgents’s capability to strike a robust balance between maximizing returns and managing risk effectively.

4. **Explainability**

A major drawback of current deep learning methods for trading is their dense, complex architectures, often rendering trading agents’ decisions indecipherable. This challenge, rooted in AI explainability, is critical for trading agents operating in real-world financial markets, where incorrect decisions can cause severe losses.

In contrast, an LLM-based agentic framework offers a transformative advantage: its decisions are communicated in natural language, enhancing interpretability. To illustrate, we provide Tradin- gAgents’s full trading log for a single day in the Appendix, showcasing its use of the ReAct-style prompting framework [(Yao et al., 2023](#_page16_x42.33_y384.82)). Each decision includes detailed reasoning, tool usage, and thoughtprocesses, enablingtraderstounderstandanddebugthesystem. Thistransparencyempowers traders to fine-tune the framework, accounting for decision factors, offering superior explainability over deep-learning trading algorithms.

2. **Discussion**

Our results demonstrate that integrating multiple specialized LLM agents and fostering agentic debate significantly enhances trading performance. This framework efficiently synthesizes diverse data sources and expert analyses, enabling trader agents to make well-informed decisions tailored to specific risk profiles. The inclusion of a reflective agent and a dedicated risk management team is pivotal in refining strategies and mitigating risks. As a result, the framework achieves exceptional returncapturewhilemaintainingstrongriskmanagementmetrics,strikinganoptimalbalancebetween maximizing rewards and minimizing risks. Additionally, the natural language-based operations of the multi-agent LLM framework ensure high explainability, giving TradingAgents a distinct advantage over traditional and deep learning methods in transparency and interoperability.

7. **Conclusion**

We introduced TradingAgents, a multi-agents LLM financial trading framework that realistically simulates a trading firm environment with multiple specialized agents engaging in agentic debates and conversations. Leveraging the advanced capabilities of LLMs to process and analyze diverse financial data sources, the framework enables more informed trading decisions while utilizing multi- agent interactions to enhance performance through comprehensive reasoning and debate before acting. By integrating agents with distinct roles and risk profiles, along with a reflective agent and a dedicated risk team, TradingAgents significantly improves trading outcomes and risk management compared to baseline models. Additionally, the collaborative nature of these agents ensures adaptability to varying market conditions. Experiments demonstrate that TradingAgents outperforms traditional trading strategies and baselines in cumulative return, Sharpe ratio, and other critical financial metrics. Future work will focus on deploying the framework in a live trading environment, expanding agent roles, and incorporating real-time data feeds to enhance performance further.

**References**

<a name="_page13_x42.33_y113.09"></a>J. Bai, S. Bai, Y. Chu, Z. Cui, K. Dang, X. Deng, Y. Fan, W. Ge, Y. Han, F. Huang, B. Hui, L. Ji, M. Li,

J. Lin, R. Lin, D. Liu, G. Liu, C. Lu, K. Lu, J. Ma, R. Men, X. Ren, X. Ren, C. Tan, S. Tan, J. Tu, P. Wang,

S. Wang, W. Wang, S. Wu, B. Xu, J. Xu, A. Yang, H. Yang, J. Yang, S. Yang, Y. Yao, B. Yu, H. Yuan,

Z. Yuan, J. Zhang, X. Zhang, Y. Zhang, Z. Zhang, C. Zhou, J. Zhou, X. Zhou, and T. Zhu. Qwen technical report, 2023. URL[ https://arxiv.org/abs/2309.16609.](https://arxiv.org/abs/2309.16609)

<a name="_page13_x42.33_y189.80"></a>A. Chowdhery, S. Narang, J. Devlin, M. Bosma, G. Mishra, A. Roberts, P. Barham, H. W. Chung,

C. Sutton, S. Gehrmann, P. Schuh, K. Shi, S. Tsvyashchenko, J. Maynez, A. Rao, P. Barnes, Y. Tay,

N. Shazeer, V. Prabhakaran, E. Reif, N. Du, B. Hutchinson, R. Pope, J. Bradbury, J. Austin, M. Isard,

G. Gur-Ari, P. Yin, T. Duke, A. Levskaya, S. Ghemawat, S. Dev, H. Michalewski, X. Garcia, V. Misra,

K. Robinson, L. Fedus, D. Zhou, D. Ippolito, D. Luan, H. Lim, B. Zoph, A. Spiridonov, R. Sepassi,

D. Dohan, S. Agrawal, M. Omernick, A. M. Dai, T. S. Pillai, M. Pellat, A. Lewkowycz, E. Moreira,

R. Child, O. Polozov, K. Lee, Z. Zhou, X. Wang, B. Saeta, M. Diaz, O. Firat, M. Catasta, J. Wei,

K. Meier-Hellstern, D. Eck, J. Dean, S. Petrov, and N. Fiedel. Palm: Scaling language modeling with pathways, 2022. URL[ https://arxiv.org/abs/2204.02311.](https://arxiv.org/abs/2204.02311)

<a name="_page13_x42.33_y320.71"></a>Y. Ding, S. Jia, T. Ma, B. Mao, X. Zhou, L. Li, and D. Han. Integrating stock features and global

information via large language models for enhanced stock return prediction, 2023. URL[ https: //arxiv.org/abs/2310.05627.](https://arxiv.org/abs/2310.05627)

<a name="_page13_x42.33_y370.32"></a>Y. Du, S. Li, A. Torralba, J. B. Tenenbaum, and I. Mordatch. Improving factuality and reasoning in language models through multiagent debate, 2023. URL[ https://arxiv.org/abs/2305.14325.](https://arxiv.org/abs/2305.14325)

<a name="_page13_x42.33_y406.39"></a>G. Fatouros, K. Metaxas, J. Soldatos, and D. Kyriazis. Can large language models beat wall street? unveiling the potential of ai in stock selection, 2024a. URL[ https://arxiv.org/abs/2401.03737.](https://arxiv.org/abs/2401.03737)

<a name="_page13_x42.33_y442.45"></a>G. Fatouros, K. Metaxas, J. Soldatos, and D. Kyriazis. Can large language models beat wall street? unveiling the potential of ai in stock selection, 2024b. URL[ https://arxiv.org/abs/2401.03737.](https://arxiv.org/abs/2401.03737)

<a name="_page13_x42.33_y478.52"></a>A. Havrilla, Y. Du, S. C. Raparthy, C. Nalmpantis, J. Dwivedi-Yu, M. Zhuravinskyi, E. Hambro,

S. Sukhbaatar, and R. Raileanu. Teaching large language models to reason with reinforcement learning, 2024. URL[ https://arxiv.org/abs/2403.04642.](https://arxiv.org/abs/2403.04642)

<a name="_page13_x42.33_y528.13"></a>S. Hong, M. Zhuge, J. Chen, X. Zheng, Y. Cheng, C. Zhang, J. Wang, Z. Wang, S. K. S. Yau, Z. Lin,

L. Zhou, C. Ran, L. Xiao, C. Wu, and J. Schmidhuber. Metagpt: Meta programming for a multi-agent collaborative framework, 2024. URL[ https://arxiv.org/abs/2308.00352.](https://arxiv.org/abs/2308.00352)

<a name="_page13_x42.33_y577.74"></a>Z. Ji, T. Yu, Y. Xu, N. Lee, E. Ishii, and P. Fung. Towards mitigating hallucination in large language

models via self-reflection, 2023. URL[ https://arxiv.org/abs/2310.06271.](https://arxiv.org/abs/2310.06271)

<a name="_page13_x42.33_y613.81"></a>K. Kirtac and G. Germano. Sentiment trading with large language models. Finance Research Letters,

62:105227, 2024. ISSN 1544-6123. doi: https://doi.org/10.1016/j.frl.2024.105227. URL[ https: //www.sciencedirect.com/science/article/pii/S1544612324002575.](https://www.sciencedirect.com/science/article/pii/S1544612324002575)

<a name="_page13_x42.33_y663.42"></a>K. J. Koa, Y. Ma, R. Ng, and T.-S. Chua. Learning to generate explainable stock predictions using self- reflective large language models, May 2024. URL[ http://dx.doi.org/10.1145/3589334.3645611.](http://dx.doi.org/10.1145/3589334.3645611)

<a name="_page14_x42.33_y87.14"></a>Y. Li, Y. Yu, H. Li, Z. Chen, and K. Khashanah. Tradinggpt: Multi-agent system with layered memory

and distinct characters for enhanced financial trading performance. arXiv preprint arXiv:2309.03736, 2023a.

<a name="_page14_x42.33_y136.51"></a>Y. Li, Y. Yu, H. Li, Z. Chen, and K. Khashanah. Tradinggpt: Multi-agent system with layered

memory and distinct characters for enhanced financial trading performance, 2023b. URL[ https: //arxiv.org/abs/2309.03736.](https://arxiv.org/abs/2309.03736)

<a name="_page14_x42.33_y185.88"></a>A. Lopez-Lira and Y. Tang. Can chatgpt forecast stock price movements? return predictability and

large language models, 2023. URL[ https://arxiv.org/abs/2304.07619.](https://arxiv.org/abs/2304.07619)

<a name="_page14_x42.33_y221.69"></a>D. Lu, H. Wu, J. Liang, Y. Xu, Q. He, Y. Geng, M. Han, Y. Xin, and Y. Xiao. Bbt-fin: Comprehensive

construction of chinese financial domain pre-trained language model, corpus and benchmark, 2023. URL[ https://arxiv.org/abs/2302.09432.](https://arxiv.org/abs/2302.09432)

<a name="_page14_x42.33_y271.06"></a>OpenAI. Learning to reason with llms - openai o1 model. [https://openai.com/index/](https://openai.com/index/learning-to-reason-with-llms/)

[learning-to-reason-with-llms/,](https://openai.com/index/learning-to-reason-with-llms/) 2024. Accessed: 2024-11-21.

<a name="_page14_x42.33_y306.88"></a>OpenAI, J. Achiam, S. Adler, S. Agarwal, L. Ahmad, I. Akkaya, F. L. Aleman, D. Almeida, J. Al-

tenschmidt, S. Altman, S. Anadkat, R. Avila, I. Babuschkin, S. Balaji, V. Balcom, P. Baltescu, H. Bao, M. Bavarian, J. Belgum, I. Bello, J. Berdine, G. Bernadett-Shapiro, C. Berner, L. Bogdonoff, O. Boiko,

M. Boyd, A.-L. Brakman, G. Brockman, T. Brooks, M. Brundage, K. Button, T. Cai, R. Campbell,

A. Cann, B. Carey, C. Carlson, R. Carmichael, B. Chan, C. Chang, F. Chantzis, D. Chen, S. Chen,

R. Chen, J. Chen, M. Chen, B. Chess, C. Cho, C. Chu, H. W. Chung, D. Cummings, J. Currier,

Y. Dai, C. Decareaux, T. Degry, N. Deutsch, D. Deville, A. Dhar, D. Dohan, S. Dowling, S. Dunning,

A. Ecoffet, A. Eleti, T. Eloundou, D. Farhi, L. Fedus, N. Felix, S. P. Fishman, J. Forte, I. Fulford, L. Gao,

E. Georges, C. Gibson, V. Goel, T. Gogineni, G. Goh, R. Gontijo-Lopes, J. Gordon, M. Grafstein,

S. Gray, R. Greene, J. Gross, S. S. Gu, Y. Guo, C. Hallacy, J. Han, J. Harris, Y. He, M. Heaton, J. Hei- decke, C. Hesse, A. Hickey, W. Hickey, P. Hoeschele, B. Houghton, K. Hsu, S. Hu, X. Hu, J. Huizinga,

S. Jain, S. Jain, J. Jang, A. Jiang, R. Jiang, H. Jin, D. Jin, S. Jomoto, B. Jonn, H. Jun, T. Kaftan, Łukasz Kaiser, A. Kamali, I. Kanitscheider, N. S. Keskar, T. Khan, L. Kilpatrick, J. W. Kim, C. Kim, Y. Kim,

J. H. Kirchner, J. Kiros, M. Knight, D. Kokotajlo, Łukasz Kondraciuk, A. Kondrich, A. Konstantini- dis, K. Kosic, G. Krueger, V. Kuo, M. Lampe, I. Lan, T. Lee, J. Leike, J. Leung, D. Levy, C. M. Li,

R. Lim, M. Lin, S. Lin, M. Litwin, T. Lopez, R. Lowe, P. Lue, A. Makanju, K. Malfacini, S. Manning,

T. Markov, Y. Markovski, B. Martin, K. Mayer, A. Mayne, B. McGrew, S. M. McKinney, C. McLeavey,

P. McMillan, J. McNeil, D. Medina, A. Mehta, J. Menick, L. Metz, A. Mishchenko, P. Mishkin,

V. Monaco, E. Morikawa, D. Mossing, T. Mu, M. Murati, O. Murk, D. Mely´ , A. Nair, R. Nakano,

R. Nayak, A. Neelakantan, R. Ngo, H. Noh, L. Ouyang, C. O’Keefe, J. Pachocki, A. Paino, J. Palermo,

A. Pantuliano, G. Parascandolo, J. Parish, E. Parparita, A. Passos, M. Pavlov, A. Peng, A. Perelman,

F. de Avila Belbute Peres, M. Petrov, H. P. de Oliveira Pinto, Michael, Pokorny, M. Pokrass, V. H. Pong, T. Powell, A. Power, B. Power, E. Proehl, R. Puri, A. Radford, J. Rae, A. Ramesh, C. Raymond,

6. Real, K. Rimbach, C. Ross, B. Rotsted, H. Roussez, N. Ryder, M. Saltarelli, T. Sanders, S. Santurkar,
6. Sastry, H. Schmidt, D. Schnurr, J. Schulman, D. Selsam, K. Sheppard, T. Sherbakov, J. Shieh,

S. Shoker, P. Shyam, S. Sidor, E. Sigler, M. Simens, J. Sitkin, K. Slama, I. Sohl, B. Sokolowsky, Y. Song,

N. Staudacher, F. P. Such, N. Summers, I. Sutskever, J. Tang, N. Tezak, M. B. Thompson, P. Tillet,

A. Tootoonchian, E. Tseng, P. Tuggle, N. Turley, J. Tworek, J. F. C. Uribe, A. Vallone, A. Vijayvergiya,

C. Voss, C. Wainwright, J. J. Wang, A. Wang, B. Wang, J. Ward, J. Wei, C. Weinmann, A. Welihinda,

P. Welinder, J. Weng, L. Weng, M. Wiethoff, D. Willner, C. Winter, S. Wolrich, H. Wong, L. Workman,

S. Wu, J. Wu, M. Wu, K. Xiao, T. Xu, S. Yoo, K. Yu, Q. Yuan, W. Zaremba, R. Zellers, C. Zhang,

M. Zhang, S. Zhao, T. Zheng, J. Zhuang, W. Zhuk, and B. Zoph. Gpt-4 technical report, 2024. URL [https://arxiv.org/abs/2303.08774.](https://arxiv.org/abs/2303.08774)

<a name="_page15_x42.33_y136.76"></a>J. S. Park, J. C. O’Brien, C. J. Cai, M. R. Morris, P. Liang, and M. S. Bernstein. Generative agents:

Interactive simulacra of human behavior, 2023. URL[ https://arxiv.org/abs/2304.03442.](https://arxiv.org/abs/2304.03442)

<a name="_page15_x42.33_y172.82"></a>C. Qian, W. Liu, H. Liu, N. Chen, Y. Dang, J. Li, C. Yang, W. Chen, Y. Su, X. Cong, J. Xu, D. Li,

Z. Liu, and M. Sun. Chatdev: Communicative agents for software development, 2024. URL [https://arxiv.org/abs/2307.07924.](https://arxiv.org/abs/2307.07924)

<a name="_page15_x42.33_y222.43"></a>J. Schulman, F. Wolski, P. Dhariwal, A. Radford, and O. Klimov. Proximal policy optimization

algorithms, 2017. URL[ https://arxiv.org/abs/1707.06347.](https://arxiv.org/abs/1707.06347)

<a name="_page15_x42.33_y258.50"></a>Y. Talebirad and A. Nadiri. Multi-agent collaboration: Harnessing the power of intelligent llm agents,

2023\. URL[ https://arxiv.org/abs/2306.03314.](https://arxiv.org/abs/2306.03314)

<a name="_page15_x42.33_y294.56"></a>X. Tang, A. Zou, Z. Zhang, Z. Li, Y. Zhao, X. Zhang, A. Cohan, and M. Gerstein. Medagents: Large

language models as collaborators for zero-shot medical reasoning, 2024. URL[ https://arxiv.org/ abs/2311.10537.](https://arxiv.org/abs/2311.10537)

<a name="_page15_x42.33_y344.18"></a>H. Touvron, L. Martin, K. Stone, P. Albert, A. Almahairi, Y. Babaei, N. Bashlykov, S. Batra, P. Bhargava,

S. Bhosale, D. Bikel, L. Blecher, C. C. Ferrer, M. Chen, G. Cucurull, D. Esiobu, J. Fernandes, J. Fu,

W. Fu, B. Fuller, C. Gao, V. Goswami, N. Goyal, A. Hartshorn, S. Hosseini, R. Hou, H. Inan,

M. Kardas, V. Kerkez, M. Khabsa, I. Kloumann, A. Korenev, P. S. Koura, M.-A. Lachaux, T. Lavril,

J. Lee, D. Liskovich, Y. Lu, Y. Mao, X. Martinet, T. Mihaylov, P. Mishra, I. Molybog, Y. Nie, A. Poulton,

J. Reizenstein, R. Rungta, K. Saladi, A. Schelten, R. Silva, E. M. Smith, R. Subramanian, X. E. Tan,

B. Tang, R. Taylor, A. Williams, J. X. Kuan, P. Xu, Z. Yan, I. Zarov, Y. Zhang, A. Fan, M. Kambadur,

S. Narang, A. Rodriguez, R. Stojnic, S. Edunov, and T. Scialom. Llama 2: Open foundation and fine-tuned chat models, 2023. URL[ https://arxiv.org/abs/2307.09288.](https://arxiv.org/abs/2307.09288)

<a name="_page15_x42.33_y475.09"></a>K. Wang, J. Li, N. P. Bhatt, Y. Xi, Q. Liu, U. Topcu, and Z. Wang. On the planning abilities of openai’s

o1 models: Feasibility, optimality, and generalizability, 2024a. URL[ https://arxiv.org/abs/2409. 19924.](https://arxiv.org/abs/2409.19924)

<a name="_page15_x42.33_y524.70"></a>M. Wang, K. Izumi, and H. Sakaji. Llmfactor: Extracting profitable factors through prompts for

explainable stock movement prediction, 2024b. URL[ https://arxiv.org/abs/2406.10811.](https://arxiv.org/abs/2406.10811)

<a name="_page15_x42.33_y560.77"></a>S. Wang, H. Yuan, L. Zhou, L. M. Ni, H.-Y. Shum, and J. Guo. Alpha-gpt: Human-ai interactive

alpha mining for quantitative investment. arXiv preprint arXiv:2308.00016, 2023. URL[ https: //arxiv.org/abs/2308.00016.](https://arxiv.org/abs/2308.00016)

<a name="_page15_x42.33_y610.38"></a>S. Wang, H. Yuan, L. M. Ni, and J. Guo. Quantagent: Seeking holy grail in trading by self-improving

large language model, 2024c. URL[ https://arxiv.org/abs/2402.03755.](https://arxiv.org/abs/2402.03755)

<a name="_page15_x42.33_y646.44"></a>S. Wu, O. Irsoy, S. Lu, V. Dabravolski, M. Dredze, S. Gehrmann, P. Kambadur, D. Rosenberg, and

G. Mann. Bloomberggpt: A large language model for finance, 2023. URL[ https://arxiv.org/abs/ 2303.17564.](https://arxiv.org/abs/2303.17564)

<a name="_page16_x42.33_y87.14"></a>Q. Xie, W. Han, X. Zhang, Y. Lai, M. Peng, A. Lopez-Lira, and J. Huang. Pixiu: A large language

model, instruction data and evaluation benchmark for finance, 2023. URL[ https://arxiv.org/ abs/2306.05443.](https://arxiv.org/abs/2306.05443)

<a name="_page16_x42.33_y136.76"></a>F. Xing. Designing heterogeneous llm agents for financial sentiment analysis, 2024. URL[ https:](https://arxiv.org/abs/2401.05799)

[//arxiv.org/abs/2401.05799.](https://arxiv.org/abs/2401.05799)

<a name="_page16_x42.33_y172.82"></a>A. Yang, B. Xiao, B. Wang, B. Zhang, C. Bian, C. Yin, C. Lv, D. Pan, D. Wang, D. Yan, F. Yang, F. Deng,

F. Wang, F. Liu, G. Ai, G. Dong, H. Zhao, H. Xu, H. Sun, H. Zhang, H. Liu, J. Ji, J. Xie, J. Dai, K. Fang,

L. Su, L. Song, L. Liu, L. Ru, L. Ma, M. Wang, M. Liu, M. Lin, N. Nie, P. Guo, R. Sun, T. Zhang, T. Li,

T. Li, W. Cheng, W. Chen, X. Zeng, X. Wang, X. Chen, X. Men, X. Yu, X. Pan, Y. Shen, Y. Wang, Y. Li,

Y. Jiang, Y. Gao, Y. Zhang, Z. Zhou, and Z. Wu. Baichuan 2: Open large-scale language models, 2023a. URL[ https://arxiv.org/abs/2309.10305.](https://arxiv.org/abs/2309.10305)

<a name="_page16_x42.33_y263.08"></a>H. Yang, X.-Y. Liu, and C. D. Wang. Fingpt: Open-source financial large language models, 2023b. URL

[https://arxiv.org/abs/2306.06031.](https://arxiv.org/abs/2306.06031)

<a name="_page16_x42.33_y299.15"></a>H. Yang, S. Yue, and Y. He. Auto-gpt for online decision making: Benchmarks and additional opinions,

2023c. URL[ https://arxiv.org/abs/2306.02224.](https://arxiv.org/abs/2306.02224)

<a name="_page16_x42.33_y335.21"></a>H. Yang, B. Zhang, N. Wang, C. Guo, X. Zhang, L. Lin, J. Wang, T. Zhou, M. Guan, R. Zhang, and C. D.

Wang. Finrobot: An open-source ai agent platform for financial applications using large language models, 2024. URL[ https://arxiv.org/abs/2405.14767.](https://arxiv.org/abs/2405.14767)

<a name="_page16_x42.33_y384.82"></a>S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. Narasimhan, and Y. Cao. React: Synergizing reasoning and

acting in language models, 2023. URL[ https://arxiv.org/abs/2210.03629.](https://arxiv.org/abs/2210.03629)

<a name="_page16_x42.33_y420.89"></a>Y. Yu, H. Li, Z. Chen, Y. Jiang, Y. Li, D. Zhang, R. Liu, J. W. Suchow, and K. Khashanah. Finmem: A

performance-enhanced llm trading agent with layered memory and character design, 2023. URL [https://arxiv.org/abs/2311.13743.](https://arxiv.org/abs/2311.13743)

<a name="_page16_x42.33_y470.50"></a>Y. Yu, Z. Yao, H. Li, Z. Deng, Y. Cao, Z. Chen, J. W. Suchow, R. Liu, Z. Cui, D. Zhang, et al. Fincon: A

synthesized llm multi-agent system with conceptual verbal reinforcement for enhanced financial decision making. arXiv preprint arXiv:2407.06567, 2024.

<a name="_page16_x42.33_y520.12"></a>B. Zhang, H. Yang, and X.-Y. Liu. Instruct-fingpt: Financial sentiment analysis by instruction tuning of

general-purpose large language models, 2023a. URL[ https://arxiv.org/abs/2306.12659.](https://arxiv.org/abs/2306.12659)

<a name="_page16_x42.33_y556.18"></a>H. Zhang, F. Hua, C. Xu, H. Kong, R. Zuo, and J. Guo. Unveiling the potential of sentiment: Can large

language models predict chinese stock price movements?, 2024a. URL[ https://arxiv.org/abs/ 2306.14222.](https://arxiv.org/abs/2306.14222)

<a name="_page16_x42.33_y605.80"></a>S. Zhang, S. Roller, N. Goyal, M. Artetxe, M. Chen, S. Chen, C. Dewan, M. Diab, X. Li, X. V.

Lin, T. Mihaylov, M. Ott, S. Shleifer, K. Shuster, D. Simig, P. S. Koura, A. Sridhar, T. Wang, and L. Zettlemoyer. Opt: Open pre-trained transformer language models, 2022. URL[ https: //arxiv.org/abs/2205.01068.](https://arxiv.org/abs/2205.01068)

23. Zhang,<a name="_page16_x42.33_y668.96"></a> L. Zhao, H. Xia, S. Sun, J. Sun, M. Qin, X. Li, Y. Zhao, Y. Zhao, X. Cai, L. Zheng, X. Wang, and B. An. A multimodal foundation agent for financial trading: Tool-augmented, diversified, and generalist, 2024b. URL[ https://arxiv.org/abs/2402.18485.](https://arxiv.org/abs/2402.18485)
24. Zhang,<a name="_page17_x42.33_y87.14"></a> Q. Yang, and D. Xu. Xuanyuan 2.0: A large chinese financial chat model with hundreds of billions parameters, 2023b. URL[ https://arxiv.org/abs/2305.12002.](https://arxiv.org/abs/2305.12002)

<a name="_page17_x42.33_y123.21"></a>T. Zhong, Z. Liu, Y. Pan, Y. Zhang, Y. Zhou, S. Liang, Z. Wu, Y. Lyu, P. Shu, X. Yu, C. Cao, H. Jiang,

H. Chen, Y. Li, J. Chen, H. Hu, Y. Liu, H. Zhao, S. Xu, H. Dai, L. Zhao, R. Zhang, W. Zhao, Z. Yang,

J. Chen, P. Wang, W. Ruan, H. Wang, H. Zhao, J. Zhang, Y. Ren, S. Qin, T. Chen, J. Li, A. H. Zidan,

1. Jahin, M. Chen, S. Xia, J. Holmes, Y. Zhuang, J. Wang, B. Xu, W. Xia, J. Yu, K. Tang, Y. Yang,
1. Sun, T. Yang, G. Lu, X. Wang, L. Chai, H. Li, J. Lu, L. Sun, X. Zhang, B. Ge, X. Hu, L. Zhang,

H. Zhou, L. Zhang, S. Zhang, N. Liu, B. Jiang, L. Kong, Z. Xiang, Y. Ren, J. Liu, X. Jiang, Y. Bao,

W. Zhang, X. Li, G. Li, W. Liu, D. Shen, A. Sikora, X. Zhai, D. Zhu, and T. Liu. Evaluation of openai o1: Opportunities and challenges of agi, 2024. URL[ https://arxiv.org/abs/2409.18486.](https://arxiv.org/abs/2409.18486)

**S1. Supplementary Materials for TradingAgents**

<a name="_page18_x66.33_y118.47"></a>**S1.1. Baseline Models**

We compare our TradingAgents framework against several baselines:

- **Buy and Hold**: Investing equal amounts in all selected stocks and holding them throughout the simulation period.
- **MACD (Moving Average Convergence Divergence)**: A trend-following momentum strategy that generates buy and sell signals based on the crossover points between the MACD line and signal line.
- **KDJ and RSI (Relative Strength Index)**: A momentum strategy combining KDJ (stochastic oscillator) and RSI (relative strength index) indicators to identify overbought and oversold conditions for trading signals.
- **ZMR (Zero Mean Reversion)**: A mean reversion trading strategy that generates signals based on price deviations from and subsequent reversions to a zero reference line.
- **SMA (Simple Moving Average)**: A trend-following strategy that generates trading signals based on crossovers between short-term and long-term moving averages.

<a name="_page18_x66.33_y340.39"></a>**S1.2. Evaluation Metrics**

To thoroughly evaluate the performance of our TradingAgents framework, we use widely recognized metrics to assess the risk management, profitability, and safety of the TradingAgents strategy in comparison to baseline approaches. Here we describe these metrics:

**S1.2.1. Cumulative Return (CR)**

The cumulative return measures the total return generated over the simulation period. It is calculated as:

Vend − Vstart

CR = × 100% (S1)

Vstart

where Vend is the portfolio value at the end of the simulation, and Vstart is the initial portfolio value.

**S1.2.2. Annualized Return (AR)**

The annualized return normalizes the cumulative return over the number of years:

1

AR = Vend N − 1 × 100% (S2)

Vstart

where N is the number of years in the simulation.

**S1.2.3. Sharpe Ratio (SR)**

The Sharpe ratio measures risk-adjusted return by comparing a portfolio’s excess return over the risk-free rate to its volatility:

R¯− Rf

SR = (S3)

*σ*

where R¯ is the average portfolio return, Rf is the risk-free rate (e.g., yield of 3-month Treasury bills), and *σ* is the standard deviation of the portfolio returns.

**S1.2.4. Maximum Drawdown (MDD)**

Maximum drawdown measures the largest peak-to-trough decline in the portfolio value:

Peak − Trough

MDD = max t t × 100% (S4)

t∈[0,T] Peakt

**S1.3. Cumulative Returns (CR) and Transaction History for AMZN and GOOGL**

We present additional figures for $AMZNand $GOOGLstocks to complement the AAPL data discussed in the main body of this paper. These supplementary visuals provide a broader perspective on the performance of our trading framework across multiple stocks, highlighting the consistency and robustness of TradingAgents’s results.



|<p>Broker (None) cash 12315.59</p><p>value 124872.71</p>||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
| - | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- |
||||||||124872\.71|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
||||||||12315\.59|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|<p>Trades - Net Profit/Loss (True) Positive</p><p>Negative</p>||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|AMZN\_data (1 Day) O:180.17 H:181.70 L:179.26 C:180.38 Volume||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|<p>BuySell (True, 0.015) buy 176.57</p><p>sell</p>||||||||180\.38||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
||||||||||||||176\.57|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
140M 120M

100M 80M 60M 40M 20M 0M

<a name="_page19_x66.33_y390.94"></a>**Fig.** S1: **TradingAgents**: Transaction History for AMZN. Detailed transaction history with Green **/** Red arrows for Long **/** Short positions.

Strategy Comparison - Cumulative Returns for AMZN![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.019.png)

Strategies\
BuyAndHoldStrategy

1\.25 MACDStrategy KDJRSIStrategy

ZMRStrategy SMAStrategy

**TradingAgents**

1\.20

1\.15

1\.10

1\.05

1\.00

2024-01-01 2024-01-15 2024-02-01 2024-02-15 2024-03-01 2024-03-15 2024-04-01

Date

<a name="_page20_x66.33_y103.59"></a>**Fig.** S2: **TradingAgents**: Cumulative Returns for AMZN. Performance comparison showing cumulative returns.



|<p>Broker (None) cash 116445.06</p><p>value 127586.29</p>||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
| - | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- | :- |
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|<p>Trades - Net Profit/Loss (True) Positive</p><p>Negative -254.11</p>||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|<p>GOOGL\_data (1 Day) O:150.48 H:151.06 L:149 Volume</p><p>BuySell (True, 0.015) buy 147.55</p><p>sell 153.32</p>|.80 C:150.56||||||153\.32 150.56|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
||||||||||||||147\.55|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
75M 60M 45M 30M 15M 0M![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.020.png)

<a name="_page20_x66.33_y443.70"></a>**Fig.** S3: **TradingAgents**: Transaction History for GOOGL. Detailed transaction history with Green **/** Red arrows for Long **/** Short positions.

Strategy Comparison - Cumulative Returns for GOOGL![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.021.png)

||<p>Strategies BuyAndHoldStrategy MACDStrategy KDJRSIStrategy ZMRStrategy SMAStrategy </p><p>**TradingAgents**</p>||||||
| :- | :- | :- | :- | :- | :- | :- |
||||||||
||||||||
||||||||
||||||||
||||||||
||||||||
1\.25

1\.20

1\.15

1\.10

1\.05

1\.00

2024-01-01 2024-01-15 2024-02-01 2024-02-15 2024-03-01 2024-03-15 2024-04-01

Date

<a name="_page21_x66.33_y82.96"></a>**Fig.** S4: **TradingAgents**: Cumulative Returns for GOOGL. Performance comparison showing cumulative returns.

By including detailed analyses for AMZN and GOOGL, we aim to demonstrate the versatility of our approach in diverse market environments, thereby reinforcing the overall effectiveness and generalizability of our methodology.

**S1.4. TradingAgents Workflow: Role Specification and Cooperation**

We offer a comprehensive overview of the various agent roles that collaborate within the TradingA- gents. These roles include the Analyst Team, Researcher Team, Trader, Risk Management Team, and Fund Manager, each dedicated to different aspects of the trading process for Apple Inc. (Ticker: AAPL) as of November 19, 2024, a recent date chosen for demonstration purposes.

By detailing the responsibilities and interactions of each agent, we demonstrate how TradingA- gents ensures thorough analysis, strategic trading decisions, and effective risk management. The collaborative structure not only enhances the system’s overall performance but also reinforces the transparency and explainability of TradingAgents, aligning with the objectives discussed in the main text. The following sections provide specific role specifications and illustrate how these agents work together to achieve robust and interpretable trading outcomes.

**TradingAgents: Market Analyst Team – Apple (AAPL)![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.022.png)**

[Market Analyst]:

================================== Report ================================== Based on the analysis of AAPL’s recent market data and selected technical

indicators , here is a detailed and nuanced report of the trends observed:![ref2]

\### Momentum Indicators

- \*\*RSI (Relative Strength Index)\*\*: The RSI values indicate significant fluctuations , with periods of overbought conditions , particularly on November 5 and November 7, where RSI values reached 100 and 89.85, respectively. This suggests strong upward price movements , potentially leading to price corrections. The RSI stabilizes towards the end of the period, indicating moderate buying momentum.

\### Trend Indicators

- \*\*ADX (Average Directional Index)\*\*: Initially , the ADX values are extremely high, indicating a strong trend, but they decline significantly , suggesting a weakening trend strength. This pattern implies a transition from a strong directional movement to a potential consolidation phase.
- \*\*Supertrend\*\*: The supertrend indicator remains constant , suggesting a stable market trend without significant volatility. This stability might indicate a consolidation phase, with the potential for future breakouts.

\### Volatility Indicators

- \*\*Bollinger Bands\*\*: The upward trend in Bollinger Bands suggests a bullish market phase with low volatility. The consistent rise in values indicates a positive market bias, with prices likely to continue rising if the trend persists.
- \*\*ATR (Average True Range)\*\*: The ATR values show an increase in market volatility , peaking on November 7. This suggests heightened market activity , with sustained volatility towards the end of the period.

\### Volume Indicators

- \*\*VR (Volume Variation Index)\*\*: The VR values highlight significant fluctuations in trading volume , with a notable spike on November 5. This indicates heightened market activity , possibly due to external factors influencing trader behavior.

\### Price Action and Support/Resistance

- \*\*CCI (Commodity Channel Index)\*\*: The CCI values indicate volatility , with several instances of overbought conditions. Peaks on November 7, November 14, and November 18 suggest strong upward price movements , which could be followed by corrections.

\### Moving Averages

- \*\*MACD (Moving Average Convergence Divergence)\*\*: The MACD values indicate a general upward trend, with some fluctuations and minor pullbacks. The increasing MACD values suggest bullish market sentiment , with the short-term moving average consistently above the long-term average.

\### Summary and Insights

The analysis of AAPL’s recent market data reveals a period of volatility with alternating phases of strong buying momentum and stabilization. The initial overbought conditions and high ADX values suggest a strong trend, which

weakens over time, indicating potential consolidation. The consistent upward

trend in Bollinger Bands and MACD values points to a bullish market sentiment , while the fluctuations in ATR and VR values highlight ongoing market

volatility.![ref2]

Traders should be cautious of potential price corrections following the overbought conditions and consider the possibility of continued volatility. The stable\
supertrend value suggests a consolidation phase, with potential for future\
breakouts. Overall , traders should remain vigilant , using these insights to adjust their strategies accordingly , while being prepared for both opportunities and risks presented by the current market conditions. ================================ Tool Calls ================================ Tool Calls:

get\_YFin\_data (call\_TuDo4m3U0lkgtV61Qpq3UIiT)

Call ID: call\_TuDo4m3U0lkgtV61Qpq3UIiT

Args:

symbol: AAPL

curr\_date: 2024-11-19

Based on the recent market data for Apple (AAPL) from November 4, 2024, to

November 18, 2024, we can observe several key trends and patterns:

1. \*\*Price Movement\*\*: AAPL has shown a general upward trend over the period, with the stock price increasing from an opening of

$220.75 on November 4 to a closing of $228.02 on November 18. The stock

experienced fluctuations , with notable highs on November

7 and November 14, reaching $227.63 and $228.87, respectively.

2. \*\*Volume Trends\*\*: Trading volume varied significantly , with a peak on November 6 at 54,561,100 shares. This suggests heightened trading activity , possibly due to market events or investor sentiment changes.
2. \*\*Dividend Payment\*\*: A dividend of $0.25 per share was paid on November 8, which might have influenced investor behavior , potentially contributing to the price movements observed around this date.
2. \*\*Volatility\*\*: The stock showed some volatility , with daily price ranges ( highs and lows) indicating active trading and potential market reactions to news or earnings reports.

To provide a comprehensive analysis , I will select a set of technical indicators

that can offer diverse insights into AAPL’s market behavior. These indicators will cover momentum , trend, volatility , volume, and price action aspects:

1. \*\*RSI (Relative Strength Index)\*\*: To assess momentum and identify overbought or oversold conditions.
1. \*\*ADX (Average Directional Index)\*\*: To evaluate the strength of the current trend.
1. \*\*Bollinger Bands\*\*: To analyze volatility and potential price breakouts.
1. \*\*MACD (Moving Average Convergence Divergence)\*\*: To identify trend changes and momentum.
1. \*\*VWMA (Volume Weighted Moving Average)\*\*: To understand price movements in relation to volume.
1. \*\*ATR (Average True Range)\*\*: To measure market volatility.
1. \*\*Supertrend\*\*: To identify trend direction and potential reversals.
1. \*\*CCI (Commodity Channel Index)\*\*: To identify cyclical trends and potential reversals.

I will now retrieve detailed reports for these indicators to provide a nuanced![ref2]

analysis of AAPL’s market conditions.

Tool Calls:

get\_stockstats\_indicators\_report (call\_rARQhoVdv6VyzI3a3R9hyhYh)

Call ID: call\_rARQhoVdv6VyzI3a3R9hyhYh

Args:

symbol: AAPL

indicator: rsi

curr\_date: 2024-11-19

get\_stockstats\_indicators\_report (call\_ODamPSS2si621zrEPb4mIitD)

Call ID: call\_ODamPSS2si621zrEPb4mIitD

Args:

symbol: AAPL

indicator: adx

curr\_date: 2024-11-19

get\_stockstats\_indicators\_report (call\_KWgyXj3GgdviC01u5KeFZkbQ)

Call ID: call\_KWgyXj3GgdviC01u5KeFZkbQ

Args:

symbol: AAPL

indicator: boll

curr\_date: 2024-11-19

get\_stockstats\_indicators\_report (call\_hshUKMGu1yvZ4m8YbJE9SaSg)

Call ID: call\_hshUKMGu1yvZ4m8YbJE9SaSg

Args:

symbol: AAPL

indicator: macd

curr\_date: 2024-11-19

get\_stockstats\_indicators\_report (call\_Iq9kq9jA2D5E7Png9lPt9bK5)

Call ID: call\_Iq9kq9jA2D5E7Png9lPt9bK5

Args:

symbol: AAPL

indicator: vwma

curr\_date: 2024-11-19

get\_stockstats\_indicators\_report (call\_SRSi644IhPjxaMdE7U8xn4a3)

Call ID: call\_SRSi644IhPjxaMdE7U8xn4a3

Args:

symbol: AAPL

indicator: atr

curr\_date: 2024-11-19

get\_stockstats\_indicators\_report (call\_Ow6VLKfP52JSFtphkJocda9f)

Call ID: call\_Ow6VLKfP52JSFtphkJocda9f

Args:

symbol: AAPL

indicator: supertrend

curr\_date: 2024-11-19

get\_stockstats\_indicators\_report (call\_FJYy18HBaxQlC8YghPphXpsB)

Call ID: call\_FJYy18HBaxQlC8YghPphXpsB

Args:

symbol: AAPL

indicator: cci

curr\_date: 2024-11-19

The data provided spans from November 4, 2024, to November 18, 2024, and includes Commodity Channel Index (CCI) values, which measure the deviation of the price from its average. The CCI values indicate the following trends and insights:

1. \*\*Initial Missing Data\*\*: On November 4, 2024, the CCI value is missing. This ![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.024.png)absence of data could be due to a lack of trading activity or data collection issues, which should be noted but does not provide insight into market conditions.
1. \*\*Positive Trend\*\*: From November 5 to November 7, there is a noticeable upward trend in CCI values , starting at 66.67 and peaking at 133.33. This suggests a strong deviation from the average price, indicating potential overbought conditions. Traders might interpret this as a signal that the market could be due for a correction or pullback.
1. \*\*Fluctuations and Correction\*\*: On November 8, the CCI decreases to 97.80, indicating a slight correction from the previous peak. This is followed by a significant drop to -9.75 on November 11, suggesting a shift towards oversold conditions. Such a rapid change could indicate increased volatility or a reaction to external market factors.
1. \*\*Recovery and Stabilization\*\*: From November 12 to November 14, the CCI values recover , moving from 10.83 to 109.26. This recovery suggests a return to positive momentum , potentially indicating renewed buying interest or stabilization in the market.
1. \*\*Moderate Fluctuations\*\*: On November 15, the CCI drops to 30.79, followed by an increase to 104.68 on November 18. These fluctuations suggest ongoing market adjustments , with the CCI remaining in positive territory , indicating that the market is still experiencing deviations above the average price.

Overall , the data reflects a period of volatility with significant swings in

market sentiment. The initial rise and subsequent fluctuations in CCI values suggest that traders should be cautious of potential overbought or oversold conditions. Monitoring these trends can help in making informed decisions about potential entry or exit points in the market.

**TradingAgents: News Analyst Team – Apple (AAPL)![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.025.png)**

[News Analyst]:

================================== Report ================================== Based on the recent news from EODHD and Finnhub , here is a comprehensive report on

the current state of the world relevant for trading and macroeconomics:

\### Global Economic and Political Environment

1. \*\*US-China Relations and Trade\*\*: There is ongoing tension between the US and China, particularly affecting companies like Apple that have significant operations in China. Jim Cramer highlighted the challenges of doing business in China amidst political tensions , which could impact Apple’s operations and stock performance.
1. \*\*US Economic Policy\*\*: The return of Donald Trump to the presidency is creating mixed reactions in the business community. Some tech executives are optimistic about potential deregulation and increased innovation , which could lead to more spending and dealmaking.
3. \*\*Inflation and Federal Reserve Policy\*\*: The October CPI inflation report showed![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.026.png) a rise to 2.6%, indicating that the Federal Reserve ’s management of inflation is on track. However , this has increased the likelihood of a pause in rate cuts, affecting market expectations and investor sentiment.

\### Sector-Specific Insights

1. \*\*Technology and AI\*\*:
   1. \*\*Apple\*\*: Apple is expanding into the smart home market with a new AI-powered device, competing with Amazon and Google. Despite strong earnings , there are concerns about overvaluation and challenges in China.
   1. \*\*Google (Alphabet)\*\*: Google is facing pressure from AI competition in the search ad business and ongoing DOJ lawsuits. Analysts have mixed views on its stock, with some not considering it a favored stock currently.
   1. \*\*Amazon\*\*: Amazon is making significant moves into full autonomy and expanding its AI services through AWS. However , its stock recently declined due to broader market corrections and Federal Reserve comments on interest rates.
1. \*\*Semiconductors\*\*:
- \*\*Taiwan Semiconductor Manufacturing Company (TSMC)\*\*: The US has finalized a $6 .6 billion subsidy for TSMC’s semiconductor production in Arizona ,

  highlighting the strategic importance of semiconductor manufacturing. Despite high demand driven by AI, TSMC is considered overvalued by some analysts due

  to geopolitical risks and its role in US-China economic competition.

3. \*\*Investment Trends\*\*:
- \*\*AI and Tech Stocks\*\*: There is a continued focus on AI-centric tech giants like Google , Meta, TSMC, Adobe, and Broadcom for potential double-digit returns. The rapid adoption of generative AI is likened to the growth of Facebook , indicating significant investment opportunities in AI technologies.

\### Market Sentiment and Investor Behavior

1. \*\*Portfolio Management\*\*: Major investment firms like Fisher Asset Management and GMO Capital have shown increased portfolio values, with significant holdings in tech giants such as Apple, Microsoft , Nvidia, Amazon, and Alphabet .
1. \*\*Investor Interest\*\*: There is heightened investor interest in Apple, as indicated by increased searches and discussions about its stock prospects. This reflects broader market attention on tech stocks amidst evolving economic conditions.

\### Conclusion

The current global economic landscape is characterized by geopolitical tensions , particularly between the US and China, impacting multinational companies. The technology sector , especially AI and semiconductor industries , remains a focal point for investors , with significant government support and market interest. Inflation management by the Federal Reserve continues to influence market

dynamics , affecting investor expectations and stock performance. Traders should consider these factors when making investment decisions , focusing on sectors with strong growth potential and navigating geopolitical risks. ================================ Tool Calls ================================ Tool Calls:

get\_EODHD\_news (call\_RCXogBfhGwyi0IuWCWhpNpQJ)

Call ID: call\_RCXogBfhGwyi0IuWCWhpNpQJ

Args:

start\_date: 2024-11-12![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.027.png)

end\_date: 2024-11-19

get\_finnhub\_news (call\_zXlMVeXHxfA2X4bDTXmIfeij) Call ID: call\_zXlMVeXHxfA2X4bDTXmIfeij

Args:

ticker: AAPL

start\_date: 2024-11-12

end\_date: 2024-11-19

get\_finnhub\_news (call\_jSKV1zMfHVqrR4GYAeEzjsoy) Call ID: call\_jSKV1zMfHVqrR4GYAeEzjsoy

Args:

ticker: TSM

start\_date: 2024-11-12

end\_date: 2024-11-19

get\_finnhub\_news (call\_7rrmR2Qo5K8O2WbxQc8zDpxB) Call ID: call\_7rrmR2Qo5K8O2WbxQc8zDpxB

Args:

ticker: GOOGL

start\_date: 2024-11-12

end\_date: 2024-11-19

get\_finnhub\_news (call\_XmPHBNBRJINGDZmBeUSnUgps) Call ID: call\_XmPHBNBRJINGDZmBeUSnUgps

Args:

ticker: AMZN

start\_date: 2024-11-12

end\_date: 2024-11-19

**TradingAgents: Social Media Analysts Team – Apple (AAPL)![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.028.png)**

[Social Media Analyst]:

================================== Report ================================== ### Comprehensive Analysis of Apple Inc. (AAPL) Social Media and Sentiment Trends

(November 12 - November 19, 2024)

\#### Social Media Insights

Upon reviewing the Reddit data for Apple Inc. over the past week, it appears there

were no significant posts or discussions captured in the dataset. This

absence of data could suggest a lack of major events or announcements that typically drive social media engagement , or it might indicate a gap in data collection. For investors , this means relying more heavily on sentiment analysis and news reports for insights during this period.

\#### Sentiment Analysis

The sentiment data for Apple Inc. (AAPL) from November 4, 2024, to November 17,

2024, reveals a dynamic landscape of public perception:

1. \*\*Positive Sentiment Peaks\*\*:
   1. \*\*November 15, 2024\*\*: A significant positive sentiment was recorded with a normalized score of 0.5445, indicating favorable news or developments.
   1. \*\*November 11, 2024\*\*: Another strong positive sentiment day with a score of 0.426, suggesting positive market reactions or announcements.
1. \*\*Moderate Positive Sentiment\*\*:
- Several days, including November 14, 13, 10, and 9, showed moderately positive ![ref3]sentiment , reflecting a generally favorable outlook towards AAPL.
3. \*\*Negative Sentiment\*\*:
   1. \*\*November 12, 2024\*\*: A negative sentiment score of -0.201 was observed , possibly due to unfavorable news or market conditions.
   1. \*\*November 4, 2024\*\*: The period started with a negative sentiment score of -0.141, indicating initial concerns or negative news.
3. \*\*Neutral Sentiment\*\*:
   1. \*\*November 17, 2024\*\*: The sentiment was neutral , suggesting a lack of significant positive or negative news impacting perceptions.
3. \*\*Engagement Levels\*\*:
- The highest engagement was noted on November 6, 2024, with a sentiment score of 0.0756, indicating increased interest or discussions , albeit with a slightly positive sentiment.

\#### Implications for Traders and Investors

- \*\*Positive Sentiment Days\*\*: The spikes in positive sentiment , particularly on November 15 and 11, could be indicative of favorable developments or market conditions that investors might want to capitalize on.
- \*\*Negative Sentiment Days\*\*: The negative sentiment on November 12 and 4 suggests caution , as these days might have been influenced by adverse news or market reactions.
- \*\*Overall Trend\*\*: The sentiment trend over the period is predominantly positive , suggesting a generally favorable outlook for AAPL. However , the occasional dips into negative sentiment highlight the importance of staying informed

  about potential risks or negative news.

In conclusion , while the lack of Reddit data limits insights from social media

discussions , the sentiment analysis provides a valuable perspective on market perceptions of Apple Inc. during this period. Investors should consider these sentiment trends alongside other market data and news to make informed decisions.

================================ Tool Calls ================================ Tool Calls:

get\_reddit\_stock\_info (call\_MfJT2mtj22GO32q7Xu5z2htS)

Call ID: call\_MfJT2mtj22GO32q7Xu5z2htS

Args:

query: Apple Inc

start\_date: 2024-11-12

end\_date: 2024-11-19

get\_EODHD\_sentiment (call\_So5Csrkq4CJKpi9jiY4ibbB2)

Call ID: call\_So5Csrkq4CJKpi9jiY4ibbB2

Args:

symbol: AAPL

curr\_date: 2024-11-19

EODHD client initialized

Reddit client initialized

Searching in subreddit: wallstreetbets

Searching in subreddit: stocks

Searching in subreddit: investing

Searching in subreddit: SecurityAnalysis

Searching in subreddit: Finance

Searching in subreddit: Economics![ref3]

The market sentiment data for AAPL over the period from November 4, 2024, to

November 17, 2024, provides insights into the prevailing attitudes and perceptions surrounding the stock. Below is a detailed analysis of the sentiment trends observed during this period:

1. \*\*November 17, 2024\*\*: The sentiment count was 1, with a normalized sentiment score of 0. This indicates a neutral sentiment on this day, suggesting no significant positive or negative sentiment was detected.
1. \*\*November 16, 2024\*\*: The sentiment count was 1, with a normalized sentiment score of -0.06. This reflects a slightly negative sentiment , although the impact appears minimal given the low count and score.
1. \*\*November 15, 2024\*\*: The sentiment count increased to 2, with a normalized sentiment score of 0.5445. This marks a significant positive sentiment , indicating a favorable perception of AAPL on this day.
1. \*\*November 14, 2024\*\*: The sentiment count was 2, with a normalized sentiment score of 0.17. This suggests a moderately positive sentiment , showing a generally favorable outlook.
1. \*\*November 13, 2024\*\*: The sentiment count was 2, with a normalized sentiment score of 0.3245. This indicates a positive sentiment , with a noticeable improvement in perception compared to the previous day.
1. \*\*November 12, 2024\*\*: The sentiment count was 2, with a normalized sentiment score of -0.201. This reflects a negative sentiment , suggesting some unfavorable views or news impacting AAPL.
1. \*\*November 11, 2024\*\*: The sentiment count was 3, with a normalized sentiment score of 0.426. This indicates a strong positive sentiment , with increased engagement and favorable perception.
1. \*\*November 10, 2024\*\*: The sentiment count was 3, with a normalized sentiment score of 0.3157. This suggests a positive sentiment , maintaining a favorable outlook similar to the previous day.
1. \*\*November 09, 2024\*\*: The sentiment count was 3, with a normalized sentiment score of 0.221. This indicates a positive sentiment , though slightly less pronounced than the previous days.
1. \*\*November 08, 2024\*\*: The sentiment count was 1, with a normalized sentiment score of 0.422. This reflects a strong positive sentiment , despite the lower engagement count.
1. \*\*November 07, 2024\*\*: The sentiment count was 2, with a normalized sentiment score of 0.144. This suggests a mildly positive sentiment , indicating a generally favorable view.
1. \*\*November 06, 2024\*\*: The sentiment count was 5, with a normalized sentiment score of 0.0756. This shows a slightly positive sentiment with the highest engagement count, suggesting increased interest or discussion around AAPL.
13. \*\*November 05, 2024\*\*: The sentiment count was 4, with a normalized sentiment ![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.030.png)score of 0.304. This indicates a positive sentiment , with a relatively high level of engagement.
13. \*\*November 04, 2024\*\*: The sentiment count was 3, with a normalized sentiment score of -0.141. This reflects a negative sentiment , suggesting some unfavorable sentiment or news at the start of the period.

\*\*Summary\*\*: Over the analyzed period, AAPL experienced fluctuations in market

sentiment , with notable positive sentiment spikes on November 15 and November 11. The sentiment was predominantly positive , with occasional dips into negative territory , particularly on November 12 and November 04. The engagement levels varied , with the highest count observed on November 06, indicating heightened interest or discussion on that day. Overall , the sentiment trend suggests a generally favorable outlook for AAPL during this period, with some days of negative sentiment that may warrant further investigation.

**TradingAgents: Fundamentals Analyst Team – Apple (AAPL)![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.031.png)**

[Fundamentals Analyst]:

================================== Report ================================== ### Comprehensive Fundamental Analysis Report for Apple Inc. (AAPL)

\#### Company Profile

Apple Inc. is a prominent player in the Technology sector, known for its

innovative products and significant market influence. Incorporated in 1980, Apple has a market capitalization of approximately $3.55 trillion USD, with 15,115.82 million shares outstanding. The company is listed on the NASDAQ under the ticker AAPL.

\#### Financial Overview

- \*\*52-Week Price Range\*\*: $164.075 - $237.49
- \*\*Price Returns\*\*:
- 5-Day: 2.805%
- 13-Week: 3.7264%
- 26-Week: 23.6604%
- 52-Week: 24.0587%
- Year-to-Date: 22.0225%
- \*\*Relative Performance\*\*: Underperformed the S&P 500 by -7.6652% over the past year.

\#### Profitability Metrics

- \*\*Gross Margin\*\*: 46.21%
- \*\*Operating Margin\*\*: 31.51%
- \*\*Net Profit Margin\*\*: 23.97%
- \*\*Return on Equity (ROE)\*\*: 164.59%
- \*\*Return on Assets (ROA)\*\*: 25.68%

\#### Growth Metrics

- \*\*EPS Growth\*\*:
- 3-Year: 2.71%
- 5-Year: 15.41%
- Quarterly YoY: -34%
- \*\*Revenue Growth\*\*:![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.032.png)
- 3-Year: 2.25%
- 5-Year: 8.49%
- Quarterly YoY: 6.07%

\#### Liquidity and Solvency

- \*\*Current Ratio\*\*: 0.8673
- \*\*Quick Ratio\*\*: 0.826
- \*\*Long-Term Debt to Equity\*\*: 1.5057
- \*\*Total Debt to Equity\*\*: 1.8723

\#### Valuation Metrics

- \*\*P/E Ratio\*\*: 37.793
- \*\*P/B Ratio\*\*: 62.2048
- \*\*P/CF Ratio\*\*: 30.0517

\#### Cash Flow and Dividends

- \*\*Cash Flow Per Share\*\*: $7.1978
- \*\*Dividend Yield\*\*: 0.4287%
- \*\*Payout Ratio\*\*: 16.25%

\#### Insider Sentiment

The insider sentiment for 2024 shows a predominantly negative trend, with several

months exhibiting the most negative Monthly Share Purchase Ratio (MSPR) possible. Notably , September showed a dramatic shift to positive sentiment , suggesting a temporary bullish outlook.

\#### Insider Transactions

Recent insider transactions include significant sales by executives:

- \*\*Chris Kondo\*\* sold 4,130 shares at $228.87.
- \*\*Arthur D. Levinson\*\* sold 150,000 shares over two transactions at prices around $224.68 to $228.66.
- \*\*Katherine L. Adams\*\* gifted 8,000 shares.

\#### Analysis and Insights

- \*\*Strengths\*\*: Apple demonstrates strong profitability and growth potential , supported by high margins and efficient asset utilization.
- \*\*Weaknesses\*\*: Liquidity constraints and high leverage pose potential risks, especially in a rising interest rate environment.
- \*\*Valuation\*\*: The stock is trading at a premium , which may be justified by its strong brand and growth prospects , but caution is advised due to potential overvaluation.

\#### Investment Considerations

- \*\*Caution on Valuation\*\*: Insider sales suggest potential concerns about stock valuation. Investors should consider reviewing their positions.
- \*\*Monitor Insider Activity\*\*: Continued monitoring of insider transactions is recommended to validate concerns about stock valuation or company performance.
- \*\*Short-term Strategy\*\*: Given the negative insider sentiment , short-term bearish strategies might be considered.

\#### Conclusion

Apple Inc. remains a financially robust company with impressive profitability and

growth metrics. However , potential investors should weigh the high valuation and leverage against the company ’s strong market position and growth potential

- The insider sentiment and transactions suggest caution , particularly

regarding stock valuation. Investors should consider these factors alongside broader![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.033.png) market conditions and company performance when making investment decisions.

================================ Tool Calls ================================ Tool Calls:

get\_finnhub\_company\_profile (call\_ScxiITX7Hf6yUuOr8g41a6WP)

Call ID: call\_ScxiITX7Hf6yUuOr8g41a6WP

Args:

ticker: AAPL

Tool Calls:

get\_finnhub\_company\_financials\_history (call\_jwgyq9XbocVWIMsOpagIArQO)

Call ID: call\_jwgyq9XbocVWIMsOpagIArQO

Args:

ticker: AAPL

freq: quarterly

end\_date: 2024-11-19

get\_finnhub\_basic\_company\_financials (call\_o2JV2EjmMuTK3Z85debseS9C)

Call ID: call\_o2JV2EjmMuTK3Z85debseS9C

Args:

ticker: AAPL

get\_finnhub\_company\_insider\_sentiment (call\_DqhGKetFeNB3zWlHLJdrTE8H)

Call ID: call\_DqhGKetFeNB3zWlHLJdrTE8H

Args:

ticker: AAPL

curr\_date: 2024-11-19

get\_finnhub\_company\_insider\_transactions (call\_v78N7hIUA4CufM6EIgErEroZ)

Call ID: call\_v78N7hIUA4CufM6EIgErEroZ

Args:

ticker: AAPL

curr\_date: 2024-11-19

**TradingAgents: Researcher Team Bullish Opinion – Apple (AAPL)![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.034.png)**

[Bullish Researcher]

Bull Researcher: Alright , let’s dive into why Apple is a solid investment

opportunity right now, despite some of the bearish concerns that have been raised.

First off, let’s talk about growth potential. Apple’s expansion into the smart

home market with a new AI-powered device is a significant move. This isn’t just about keeping up with competitors like Amazon and Google; it’s about leveraging their existing ecosystem to create a seamless user experience. Apple’s ability to integrate new products into its ecosystem is a huge competitive advantage. This isn’t just a new product; it’s a strategic expansion that could drive significant revenue growth.

Now, I know the bear argument might point to challenges in China due to

geopolitical tensions. But let’s not forget that Apple has a history of navigating complex international markets successfully. Their strong brand loyalty and innovative product lineup give them a buffer against these challenges. Plus, the global demand for Apple’s products remains robust, as evidenced by their impressive revenue growth metrics over the past five years.

Speaking of financials , Apple’s profitability metrics are outstanding. With a![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.035.png)

gross margin of 46.21% and a net profit margin of 23.97%, Apple is operating at a level of efficiency that most companies can only dream of. Yes, the P/E ratio is high, but that’s often the case with companies that have strong growth prospects and a dominant market position. The high valuation reflects investor confidence in Apple’s future earnings potential.

The bear argument might also highlight insider sales as a red flag. However , insider sales can happen for a variety of reasons , not necessarily because insiders believe the stock is overvalued. It’s crucial to look at the broader

picture. The fact that major investment firms are increasing their holdings in Apple suggests that institutional investors see long-term value here.

Let’s address the liquidity and leverage concerns. While Apple’s current and quick

ratios are below 1, indicating potential liquidity constraints , it’s

important to remember that Apple generates substantial cash flow. Their cash flow per share is strong , and they have a history of effectively managing

their debt. This financial strength gives them the flexibility to invest in growth opportunities and weather economic uncertainties.

Finally , let’s talk about market sentiment. Despite some fluctuations , the overall sentiment trend for Apple is predominantly positive. The spikes in positive sentiment , particularly on days with favorable news, indicate that the market

is generally optimistic about Apple’s prospects. This aligns with the

technical indicators showing a bullish market sentiment , such as the upward trend in Bollinger Bands and MACD values.

In conclusion , while there are always risks to consider , Apple’s strong growth

potential , competitive advantages , and robust financial performance make it a compelling investment opportunity. The bearish concerns , while valid, are outweighed by the company ’s strengths and the positive market sentiment. Investing in Apple means betting on a company with a proven track record of innovation and success.

**TradingAgents: Researcher Team Bearish Opinion – Apple (AAPL)![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.036.png)**

[Bearish Researcher]

Bear Researcher: Alright , let’s dive into why investing in Apple right now might

be riskier than it seems, despite the bullish enthusiasm.

First, let’s tackle the growth potential argument. Yes, Apple is expanding into the smart home market with a new AI-powered device, but let’s not overlook the

intense competition from established players like Amazon and Google. These companies have been in the smart home space for years and have a significant head start. Apple’s late entry could mean they face an uphill battle to capture market share, and there’s no guarantee that their ecosystem will be enough to sway consumers away from competitors.

Now, about the geopolitical tensions with China. The bullish view suggests Apple

can navigate these challenges due to brand loyalty and innovation. However , the reality is that geopolitical tensions can lead to sudden regulatory changes , tariffs , or even consumer boycotts , which could severely impact Apple ’s supply chain and sales in one of its largest markets. The risks here are not just theoretical; they’re very real and could have substantial financial ![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.037.png)implications.

Regarding financials , while Apple’s profitability metrics are indeed strong, the

high PE ratio is a red flag. It suggests that the stock is priced for perfection , leaving little room for error. Any misstep or negative news could lead to a significant correction. The bullish argument glosses over this by attributing it to investor confidence , but high valuations can also indicate overvaluation , which is a risk in itself.

Insider sales are another point of concern. While it’s true that insiders sell for various reasons , the pattern of significant sales by top executives could

indicate a lack of confidence in the stock’s current valuation. This isn’t something to dismiss lightly , especially when combined with the negative insider sentiment observed throughout the year.

On liquidity and leverage , the bullish argument mentions Apple’s strong cash flow, but the current and quick ratios below 1 are concerning. This indicates

potential liquidity issues , which could be problematic if economic conditions worsen or if Apple needs to make significant investments to stay competitive. High leverage also means increased risk, especially in a rising interest rate environment where debt servicing costs could escalate.

Finally , let’s address market sentiment. While there have been spikes in positive sentiment , the overall picture is mixed, with notable negative sentiment days.

This volatility in sentiment suggests that the market is uncertain about Apple’s future , which aligns with the technical indicators showing potential for price corrections and ongoing volatility.

In conclusion , while Apple is undoubtedly a strong company with a history of

success , the current investment landscape is fraught with risks. High valuation , geopolitical tensions , insider sales, and liquidity concerns all point to potential vulnerabilities. The bullish arguments , while highlighting Apple’s strengths , don’t fully account for these risks. As a bear, I believe it’s crucial to approach Apple with caution , considering the potential for downside in the current market environment.

**TradingAgents: Risk Management Team Aggressive Agent – Apple (AAPL)![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.038.png)**

[Risky Analyst]

Risky Analyst: Let’s dive into why a high-reward, high-risk approach with Apple Inc. (AAPL) is the optimal strategy right now, especially when considering the

current market dynamics and sentiment.

First, let’s address the conservative analyst ’s likely concerns about the potential for price corrections due to overbought conditions and high

valuation. While it’s true that the RSI and CCI indicate overbought conditions , these are signs of strong upward momentum. The market is clearly bullish , as

evidenced by the consistent upward trend in Bollinger Bands and MACD values. This bullish sentiment is further supported by the positive social media sentiment peaks on November 15 and 11, suggesting favorable developments that could drive the stock higher. By focusing too much on potential corrections , the conservative view might miss the opportunity to capitalize on this

momentum.![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.039.png)

Now, regarding the neutral analyst ’s probable stance on the weakening trend strength indicated by the ADX and the stable supertrend suggesting consolidation , these are precisely the conditions that set the stage for potential breakouts. The market ’s current consolidation phase, coupled with

the heightened volatility indicated by the ATR, presents a ripe environment

for significant upward movements. The neutral perspective might overlook the potential for these breakouts , which could lead to substantial gains for those willing to take the risk.

Furthermore , the global economic and political environment , while presenting challenges such as US-China tensions , also offers opportunities. The return of

Donald Trump and potential deregulation could spur innovation and spending in the tech sector , benefiting companies like Apple. The expansion into the

smart home market with AI-powered devices positions Apple to capture new growth areas, which the conservative and neutral views might underestimate.

From a fundamental standpoint , Apple’s strong profitability metrics , such as a

46\.21% gross margin and a 164.59% ROE, highlight its ability to generate significant returns. While concerns about liquidity and leverage exist, Apple’ s robust cash flow and market position provide a buffer against these risks. The conservative focus on insider sales and high valuation might miss the broader picture of Apple’s strategic positioning and growth potential.

In conclusion , while there are risks associated with investing in Apple at this

juncture , the potential rewards far outweigh them. The market’s bullish sentiment , coupled with Apple’s strategic initiatives and strong financials , presents a compelling case for a high-reward approach. By embracing this strategy , traders can position themselves to outpace market norms and capitalize on the opportunities that others might overlook due to excessive caution.

Safe Analyst: Let’s take a closer look at the arguments presented by the Risky Analyst and why a conservative approach is more prudent in this situation.

**TradingAgents: Risk Management Team Conservative Agent – Apple (AAPL)![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.040.png)**

[Safe Analyst]

Firstly , the Risky Analyst highlights the overbought conditions indicated by the RSI and CCI as signs of strong upward momentum. However , these indicators also

suggest that the stock is potentially overvalued and ripe for a correction. Ignoring these signals could lead to significant losses if the market corrects , which is a real possibility given the high volatility indicated by the ATR. The conservative approach would be to wait for these indicators to stabilize before making any aggressive moves, thereby minimizing the risk of buying at a peak.

Regarding the potential for breakouts during the consolidation phase, as suggested by the ADX and supertrend indicators , it’s important to remember that

consolidation can also lead to breakdowns , not just breakouts. The heightened volatility and fluctuating volume further increase the uncertainty. A cautious strategy would involve waiting for clearer signals of a breakout before committing significant resources , thus protecting the firm’s assets from

unnecessary exposure to risk.![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.041.png)

The Risky Analyst also mentions the potential benefits of deregulation and Apple’s expansion into new markets. While these are positive developments , they are speculative and contingent on numerous external factors , such as geopolitical

tensions and economic policies , which are currently unpredictable. The ongoing US-China tensions , for instance , pose a significant risk to Apple’s

operations and supply chain, which could negatively impact its stock performance. A conservative approach would involve closely monitoring these developments and adjusting strategies accordingly , rather than making

premature investments based on uncertain outcomes.

From a fundamental perspective , while Apple’s profitability metrics are indeed

strong, the high valuation and insider sales are red flags that cannot be ignored. The P/E and P/B ratios suggest that the stock is trading at a premium , which could lead to a sharp decline if market sentiment shifts. Insider sales further indicate that those closest to the company might believe the stock is overvalued. A conservative strategy would involve reassessing the valuation and waiting for a more favorable entry point, ensuring that investments are made at a sustainable price level.

In conclusion , while the potential for high rewards exists, the associated risks are substantial and could jeopardize the firm’s assets. A conservative

approach prioritizes stability and long-term growth by carefully evaluating

market conditions and avoiding unnecessary exposure to volatility. By focusing on risk mitigation and asset protection , we can ensure steady, reliable

growth without succumbing to the allure of short-term gains that may not be sustainable.

Neutral Analyst: Alright , let’s dive into this discussion and find a balanced

perspective between the Risky and Safe Analysts ’ viewpoints on Apple Inc. ( AAPL).

**TradingAgents: Risk Management Team Neutral Agent – Apple (AAPL)![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.042.png)**

[Neutral Analyst]

Starting with the Risky Analyst ’s perspective , there’s a strong emphasis on the bullish momentum and potential for high rewards. It’s true that indicators

like the RSI and MACD suggest upward momentum , and the positive sentiment

peaks could signal favorable developments. However , the Risky Analyst might be underestimating the potential for a market correction. The overbought conditions and high volatility indicated by the ATR suggest that the market could swing either way. While the potential for breakouts exists, it’s crucial to remember that these conditions can also lead to significant downturns. A more balanced approach would involve setting stop-loss orders or considering options strategies to hedge against potential losses while still participating in the upside.

On the other hand, the Safe Analyst is right to point out the risks associated with overvaluation and insider sales. The high P/E and P/B ratios do suggest that Apple might be trading at a premium , and insider sales could be a red

flag. However , the Safe Analyst might be overly cautious by suggesting waiting for a more favorable entry point. Given Apple’s strong profitability metrics and strategic initiatives , there could be missed opportunities if one waits

too long. Instead , a moderate approach could involve gradually building a ![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.043.png)position in Apple, allowing for dollar-cost averaging to mitigate the risk of buying at a peak.

Regarding the geopolitical and economic factors , both analysts have valid points. The Risky Analyst sees potential in deregulation and Apple’s expansion into

new markets , while the Safe Analyst rightly highlights the unpredictability of these factors. A balanced strategy would involve closely monitoring these

developments and being ready to adjust positions as new information becomes available. Diversifying investments across different sectors or geographies could also help mitigate the risks associated with geopolitical tensions.

In conclusion , a moderate risk strategy would involve a careful balance of taking

advantage of Apple’s growth potential while safeguarding against extreme volatility. This could include using a mix of technical analysis to time entries and exits, fundamental analysis to assess long-term value, and diversification to spread risk. By adopting this balanced approach , investors can aim for steady growth without exposing themselves to unnecessary risks.

**TradingAgents: Fund Manager – Apple (AAPL)![](Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.044.png)**

[Manager]

Based on the investment plan provided and the analysis of both bullish and bearish

perspectives , I concur with the recommendation to \*\*Buy\*\* Apple (AAPL) shares

- Here is a summary of the rationale:
1. \*\*Strong Fundamentals and Growth Prospects:\*\* Apple’s consistent earnings growth and robust market capitalization highlight its financial strength and potential for continued expansion. The company ’s innovation , particularly in AI and other cutting -edge technologies , positions it well for future growth.
1. \*\*Innovation and Market Leadership:\*\* Apple’s commitment to innovation and maintaining a competitive edge through its ecosystem strengthens its market position. This is crucial in sustaining long-term growth and profitability.
1. \*\*Resilience to External Risks:\*\* Despite concerns about geopolitical tensions and financial risks, Apple’s strategic partnerships and global supply chain management mitigate these challenges effectively.
1. \*\*Positive Market Sentiment:\*\* The overall positive sentiment towards Apple, despite some volatility , indicates strong investor confidence in its long-term prospects.

While the concerns about high valuation ratios and insider selling are valid, they are outweighed by Apple’s strong fundamentals and growth potential. The high

P/E ratio can be justified by Apple’s market leadership and sustained growth trajectory. Additionally , the proposed risk management strategies , such as setting stop-loss orders and maintaining a diversified portfolio , provide a prudent approach to mitigating potential risks.

Therefore , considering the comprehensive analysis and the investment plan’s

emphasis on long-term growth and resilience , I recommend a \*\*Buy\*\* for Apple shares.
40

[ref1]: Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.003.png
[ref2]: Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.023.png
[ref3]: Aspose.Words.5f3f0ef9-be47-4b1e-af8a-4f9ac51df498.029.png
