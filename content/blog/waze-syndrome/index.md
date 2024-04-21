+++
title = "AI: WAZE Syndrome and Bias Sensitivity"
date = 2024-03-06
updated = 2024-03-29
description = "If we were to use generative AI in the same way we use Waze, we would end up accepting the ideas provided by the AI without thinking and allowing ourselves to be influenced by the biases, more or less deliberate, of those who design them. The 'Waze syndrome’ is a metaphor that  illustrates our propensity to depend on AI without questioning the underlying datasets or the motivations of its creators."

[taxonomies]
tags = ["AI", "bias", "Responsible AI", "AI Sovereignty"]

[extra]
giscus = true
copy_button = true
footnote_backlinks = true
+++

<div style="overflow: auto;">
    <img src="/blog/waze-syndrome/img/waze.png" style="float: left; margin-top: 20px; margin-right: 20px; width: 30%; vertical-align: top;">
    <div style="display: block;">
        <p>I recently gave an introductory AI course to a Bachelor's degree class at the University of Cergy (France), where the topic of discussion was how AI could influence human decision-making capabilities and free will. The comparison of how we use Waze, and navigation apps in general, is telling: today, we blindly trust these applications! They are efficient most of the time, so we stop thinking and never fail to turn them on for even the shortest journeys. But perhaps they lead us on paths that serve interests other than just getting us efficiently from point A to point B. Maybe they have us miss certain gas stations or other points of interest that could be beneficial or more economical for us. This reliance raises questions about whether we are ceding too much control to these algorithms, potentially overlooking alternative routes or experiences that could offer more than just efficiency. Such scenarios underscore the importance of maintaining a balance between leveraging technological conveniences and retaining our ability to make independent and informed decisions.</p>
    </div>
</div>

## Generative AI Bias
The 'WAZE Syndrome'[^1] is a metaphor describing our tendency to blindly follow technologies, especially those claiming to simplify our decision-making processes, like the WAZE navigation app. This syndrome may extend to our interactions with generative artificial intelligences (such as GPT-4, DALL-E, etc.), which are trained on vast data sets and produce content that appears persuasive.

Generative AIs, though sophisticated, are not free from bias. These biases may stem from the selection of training data, how algorithms interpret this data, and the implicit or explicit objectives of those who develop and utilize them. For instance, if an AI is predominantly trained on data from Western sources, it might not be representative of diverse global perspectives.

## The Impact of AI Bias and the Importance of Critical Engagement
By delegating our thinking and decision-making to these systems, we risk being subtly influenced by these biases. This can insidiously shape our worldview and values. For example, if a generative AI predominantly produces images in a style aligning with certain aesthetic standards, users may subconsciously start to favor those standards over others. Similarly, if a generative AI writes primarily in a particular style or tone, it could influence how users expect information to be presented, potentially excluding styles that might be more nuanced or accurate in some contexts.

Below is an image generated at the beginning of March 2024 by DALL-E from this message: "Draw me a crowd facing me". The result is a crowd of people facing the observer, but they are all white. This example illustrates how bias can manifest itself in the results of generative AI:
[![DALL-E Crowd](/blog/waze-syndrome/img/crowd.webp)](/blog/waze-syndrome/img/crowd.webp)

Understanding AI bias sensitivity is important for responsible use. It is vital to question the results provided by AI, understand the limits of these technologies, and recognize that our own judgment remains an integral part of the decision-making process. This requires continuous education on how AIs function, their strengths and weaknesses, and a commitment to diversifying the datasets and perspectives incorporated into the AI development process.

It becomes essential to cultivate advanced digital literacy, where the user is not just a consumer of technology but also a conscious actor in its influence. This involves developing the ability to question and evaluate the information produced by AI, to recognize the subtle inflections of present biases, and to appreciate the multitude of perspectives that humans can (still) offer compared to the machine. Instead of being unreservedly guided by AI suggestions, a stance of critical collaboration should be adopted, where humans guide AI as much as AI assists humans.

This synergy between human and artificial intelligence must be fostered with discernment to avoid falling into a technological dependence where human judgment is neglected.


## AI sovereignty and societal model
In February 2024, in an even more demonstrative way, Google's Gemini AI displayed representation biases that we would describe as "very demonstrative" (to the point where they become caricatures)[^2].
This radical orientation of the results of AI demonstrates, if proof were needed, the extent to which mastery of algorithms is a determining factor in the representation of the world conveyed by the companies that create them. This is where the importance of AI sovereignty comes into its own[^3]!

The quest for an ethical, representative and neutral AI illustrates a societal ideal which, while admirable, comes up against the intrinsic diversity of human perspectives, which are sometimes irreconcilable. This diversity, rich in history and culture, colours our societies and guides our perception of the world, our ideas and our ethical constructs. Attempting to capture the essence of this diversity with the aim of absolute neutrality may prove to be an illusion, potentially sacrificing relevance, realism, subtlety and creativity on the altar of a precarious consensus.

The question of AI sovereignty is therefore not only a question of technological mastery, but also a question of societal model. It is a question of the place we want to give to the human in the face of the machine, of the balance we want to maintain between the efficiency of the algorithms and the richness of human judgment. It is a question of the values we want to convey through these technologies, and the world we want to build with them.


# A prelude to further exploration 
Our journey begins with the exploration of the "WAZE Syndrome", a metaphor highlighting our propensity to blindly follow technologies, especially those designed to streamline our decision-making processes. This metaphor extends to generative artificial intelligences which carry inherent biases from their training data, algorithmic interpretations, and the objectives of their developers. These biases have the potential to subtly yet profoundly influence our worldview and values.

In facing the intricate dilemma of bias in artificial intelligence, we find ourselves at a crossroads between two philosophically divergent paths. On one hand, acknowledging and accepting the inherent biases within AI systems offers a pragmatic approach. It admits the impossibility of creating a perfectly neutral entity given the diverse and often contradictory tapestry of human culture and ethics. Recognizing biases not only reflects a commitment to transparency but also an acknowledgment of the complexity and richness of human perspectives.

On the other hand, striving for an ethically neutral AI represents an idealistic pursuit, one that seeks to elevate technology beyond the parochial and into a realm of universal values and principles. However, this endeavor itself harbors a paradox, as the very act of defining neutrality is influenced by specific ethical viewpoints, thus introducing a new form of bias. The quest for neutrality, in its essence, might inadvertently distance AI from the multifaceted realities of human societies.

In the next post, we will try to develop these notions, looking in more detail at the implications of each position and examining their impact on the future of artificial intelligence and its role in our society.

---
[^1]: This article was inspired by a discussion with my students in december 2023. The term "WAZE Syndrome" was coined during this discussion.
 
[^2]: Google explains the matter in this blog post: [Gemini image generation got it wrong. We'll do better.](https://blog.google/products/gemini/gemini-image-generation-issue/) Here is a Gimini illustration of 1943 German soldiers, witch do not represent the reality of the time and which has, in part, provoked criticism:
[![Google Gemini](/blog/waze-syndrome/img/german_soldiers.avif)](/blog/waze-syndrome/img/german_soldiers.avif)

[^3]: And once again this is an opportunity to broaden the question of the trust we place in this type of company: here the error is gross, certainly due to the fact that the AI algorithms, ethical behaviour filters and default prompts are new and not properly mastered. But what about in areas that are better mastered, where we have let our guard down:
  - filtering and ordering search results
  - managing and classifying our e-mails
  - personalized advertising and content recommendations
  - content moderation and the detection of harmful online behavior
  - etc.