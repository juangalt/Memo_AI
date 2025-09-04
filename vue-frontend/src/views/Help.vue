<template>
  <Layout>
    <div class="max-w-4xl mx-auto">
      <div class="bg-white rounded-lg shadow-lg p-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-8">
          📚 Help & Documentation
        </h1>

        <!-- Quick Start -->
        <div class="mb-12">
          <h2 class="text-2xl font-semibold text-gray-900 mb-4">🚀 Quick Start</h2>
          <div class="bg-blue-50 rounded-lg p-6">
            <ol class="list-decimal list-inside space-y-3 text-gray-700">
              <li>Go to <strong>Text Input</strong> and paste your business memo or professional text</li>
              <li>Click <strong>Submit for Evaluation</strong> and wait for AI analysis</li>
              <li>View your <strong>Overall Feedback</strong> with comprehensive scores and insights</li>
              <li>Review detailed <strong>Rubric Scores</strong> for targeted improvements</li>
              <li>Analyze <strong>Segment Feedback</strong> for specific text sections</li>
            </ol>
          </div>
        </div>

        <!-- Features Overview -->
        <div class="mb-12">
          <h2 class="text-2xl font-semibold text-gray-900 mb-4">✨ Key Features</h2>
          <div class="grid md:grid-cols-2 gap-6">
            <div class="bg-gray-50 rounded-lg p-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-3">📝 Text Input</h3>
              <p class="text-gray-600 mb-3">Submit any business memo, report, proposal, or professional text for evaluation.</p>
              <ul class="text-sm text-gray-600 space-y-1">
                <li>• Maximum 10,000 characters</li>
                <li>• Real-time character counter</li>
                <li>• Progress tracking during analysis</li>
                <li>• Support for multiple languages</li>
              </ul>
            </div>
            <div class="bg-gray-50 rounded-lg p-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-3">📊 Overall Feedback</h3>
              <p class="text-gray-600 mb-3">Get comprehensive evaluation with weighted overall score and detailed insights.</p>
              <ul class="text-sm text-gray-600 space-y-1">
                <li>• Weighted overall score (1.0-5.0 scale)</li>
                <li>• Key strengths identification</li>
                <li>• Improvement opportunities</li>
                <li>• Actionable recommendations</li>
              </ul>
            </div>
            <div class="bg-gray-50 rounded-lg p-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-3">🎯 Rubric Scores</h3>
              <p class="text-gray-600 mb-3">Detailed breakdown across 4 core business writing criteria with weighted scoring.</p>
              <ul class="text-sm text-gray-600 space-y-1">
                <li>• 4 weighted criteria (total 100%)</li>
                <li>• Individual scores with justifications</li>
                <li>• Targeted improvement areas</li>
                <li>• Professional writing standards</li>
              </ul>
            </div>
            <div class="bg-gray-50 rounded-lg p-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-3">🔍 Segment Analysis</h3>
              <p class="text-gray-600 mb-3">Detailed feedback on specific text sections with questions and suggestions.</p>
              <ul class="text-sm text-gray-600 space-y-1">
                <li>• Section-by-section analysis</li>
                <li>• Specific improvement questions</li>
                <li>• Actionable suggestions</li>
                <li>• Context-aware feedback</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Evaluation Rubric -->
        <div class="mb-12">
          <h2 class="text-2xl font-semibold text-gray-900 mb-4">📋 Evaluation Rubric</h2>
          <div class="bg-green-50 rounded-lg p-6 mb-6">
            <p class="text-gray-700 mb-4">
              Your business memo is evaluated across 4 core criteria using a weighted scoring system (1-5 scale):
            </p>
            <div class="grid md:grid-cols-2 gap-4 text-sm">
              <div>
                <span class="font-semibold">1 - Poor:</span> Significant issues, needs major revision
              </div>
              <div>
                <span class="font-semibold">2 - Below Average:</span> Several areas need improvement
              </div>
              <div>
                <span class="font-semibold">3 - Average:</span> Adequate but could be enhanced
              </div>
              <div>
                <span class="font-semibold">4 - Good:</span> Well-written with minor improvements possible
              </div>
              <div class="md:col-span-2">
                <span class="font-semibold">5 - Excellent:</span> Outstanding quality, professional standard
              </div>
            </div>
          </div>

          <div class="space-y-6">
            <!-- Structure -->
            <div class="border-l-4 border-blue-500 pl-6">
              <div class="flex items-center justify-between mb-2">
                <h3 class="text-lg font-semibold text-gray-900">📐 Structure (25% Weight)</h3>
                <span class="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded-full">25%</span>
              </div>
              <p class="text-gray-600 mb-3 font-medium">Pyramid principle, SCQA framework, clarity of opportunity, clear ask</p>
              <p class="text-gray-600 mb-2">Evaluates the organization, logical flow, and structural clarity of your memo.</p>
              <ul class="text-sm text-gray-600 space-y-1">
                <li>• <strong>Pyramid Principle:</strong> Main message first, supporting details follow</li>
                <li>• <strong>SCQA Framework:</strong> Situation, Complication, Question, Answer structure</li>
                <li>• <strong>Clear Opportunity:</strong> Well-defined problem or opportunity statement</li>
                <li>• <strong>Clear Ask:</strong> Specific request or recommendation</li>
                <li>• Logical organization and effective use of headings</li>
              </ul>
            </div>

            <!-- Arguments and Evidence -->
            <div class="border-l-4 border-green-500 pl-6">
              <div class="flex items-center justify-between mb-2">
                <h3 class="text-lg font-semibold text-gray-900">💡 Arguments and Evidence (30% Weight)</h3>
                <span class="bg-green-100 text-green-800 text-xs font-medium px-2 py-1 rounded-full">30%</span>
              </div>
              <p class="text-gray-600 mb-3 font-medium">Logic, financial metrics, credible evidence</p>
              <p class="text-gray-600 mb-2">Assesses the strength of your arguments and supporting evidence.</p>
              <ul class="text-sm text-gray-600 space-y-1">
                <li>• <strong>Logical Reasoning:</strong> Clear cause-and-effect relationships</li>
                <li>• <strong>Financial Metrics:</strong> Relevant KPIs, ROI calculations, cost-benefit analysis</li>
                <li>• <strong>Credible Evidence:</strong> Data, research, expert opinions, case studies</li>
                <li>• <strong>Persuasive Arguments:</strong> Compelling rationale for recommendations</li>
                <li>• Factual accuracy and reliable sources</li>
              </ul>
            </div>

            <!-- Strategic Alignment -->
            <div class="border-l-4 border-purple-500 pl-6">
              <div class="flex items-center justify-between mb-2">
                <h3 class="text-lg font-semibold text-gray-900">🎯 Strategic Alignment (25% Weight)</h3>
                <span class="bg-purple-100 text-purple-800 text-xs font-medium px-2 py-1 rounded-full">25%</span>
              </div>
              <p class="text-gray-600 mb-3 font-medium">Help achieve strategic goals 1, 2, 3</p>
              <p class="text-gray-600 mb-2">Measures how well your memo aligns with organizational objectives.</p>
              <ul class="text-sm text-gray-600 space-y-1">
                <li>• <strong>Goal Alignment:</strong> Clear connection to strategic objectives</li>
                <li>• <strong>Priority Support:</strong> Addresses high-impact strategic initiatives</li>
                <li>• <strong>Resource Optimization:</strong> Efficient use of organizational resources</li>
                <li>• <strong>Stakeholder Value:</strong> Benefits for key stakeholders</li>
                <li>• Long-term strategic impact</li>
              </ul>
            </div>

            <!-- Implementation and Risks -->
            <div class="border-l-4 border-orange-500 pl-6">
              <div class="flex items-center justify-between mb-2">
                <h3 class="text-lg font-semibold text-gray-900">⚙️ Implementation and Risks (20% Weight)</h3>
                <span class="bg-orange-100 text-orange-800 text-xs font-medium px-2 py-1 rounded-full">20%</span>
              </div>
              <p class="text-gray-600 mb-3 font-medium">Feasibility, risk assessment, implementation plan</p>
              <p class="text-gray-600 mb-2">Reviews the practicality and risk management of your proposal.</p>
              <ul class="text-sm text-gray-600 space-y-1">
                <li>• <strong>Feasibility:</strong> Realistic implementation timeline and resources</li>
                <li>• <strong>Risk Assessment:</strong> Identification and mitigation of potential risks</li>
                <li>• <strong>Implementation Plan:</strong> Clear steps, milestones, and responsibilities</li>
                <li>• <strong>Resource Requirements:</strong> Budget, personnel, and technology needs</li>
                <li>• Contingency planning and alternatives</li>
              </ul>
            </div>
          </div>

          <!-- Scoring System -->
          <div class="bg-blue-50 rounded-lg p-6 mt-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-3">📊 Scoring System</h3>
            <div class="grid md:grid-cols-2 gap-4 text-sm">
              <div>
                <p class="font-semibold text-gray-700 mb-2">Weighted Calculation:</p>
                <ul class="text-gray-600 space-y-1">
                  <li>• Structure: 25% × Score</li>
                  <li>• Arguments & Evidence: 30% × Score</li>
                  <li>• Strategic Alignment: 25% × Score</li>
                  <li>• Implementation & Risks: 20% × Score</li>
                </ul>
              </div>
              <div>
                <p class="font-semibold text-gray-700 mb-2">Example:</p>
                <ul class="text-gray-600 space-y-1">
                  <li>• Structure: 4 × 0.25 = 1.0</li>
                  <li>• Arguments: 5 × 0.30 = 1.5</li>
                  <li>• Alignment: 4 × 0.25 = 1.0</li>
                  <li>• Implementation: 3 × 0.20 = 0.6</li>
                  <li><strong>Overall: 4.1</strong></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- Tips for Better Results -->
        <div class="mb-8">
          <h2 class="text-2xl font-semibold text-gray-900 mb-4">💡 Tips for Better Results</h2>
          <div class="bg-yellow-50 rounded-lg p-6">
            <ul class="space-y-3 text-gray-700">
              <li class="flex items-start">
                <span class="text-yellow-600 mr-2 mt-1">•</span>
                <span><strong>Start with the main message:</strong> Use the pyramid principle to lead with your key recommendation</span>
              </li>
              <li class="flex items-start">
                <span class="text-yellow-600 mr-2 mt-1">•</span>
                <span><strong>Follow SCQA structure:</strong> Clearly establish the situation, complication, question, and answer</span>
              </li>
              <li class="flex items-start">
                <span class="text-yellow-600 mr-2 mt-1">•</span>
                <span><strong>Support with data:</strong> Include relevant financial metrics and credible evidence</span>
              </li>
              <li class="flex items-start">
                <span class="text-yellow-600 mr-2 mt-1">•</span>
                <span><strong>Link to strategy:</strong> Show how your proposal supports organizational goals</span>
              </li>
              <li class="flex items-start">
                <span class="text-yellow-600 mr-2 mt-1">•</span>
                <span><strong>Address risks:</strong> Include realistic implementation plans and risk mitigation strategies</span>
              </li>
              <li class="flex items-start">
                <span class="text-yellow-600 mr-2 mt-1">•</span>
                <span><strong>Be specific:</strong> Include concrete details, timelines, and clear next steps</span>
              </li>
            </ul>
          </div>
        </div>

        <!-- Language Support -->
        <div class="mb-8">
          <h2 class="text-2xl font-semibold text-gray-900 mb-4">🌍 Language Support</h2>
          <div class="bg-gray-50 rounded-lg p-6">
            <p class="text-gray-700 mb-4">
              Memo AI Coach supports multiple languages for global business communication:
            </p>
            <div class="grid md:grid-cols-2 gap-4">
              <div class="flex items-center space-x-3">
                <span class="text-2xl">🇺🇸</span>
                <div>
                  <h4 class="font-semibold text-gray-900">English</h4>
                  <p class="text-sm text-gray-600">Primary language with full rubric support</p>
                </div>
              </div>
              <div class="flex items-center space-x-3">
                <span class="text-2xl">🇪🇸</span>
                <div>
                  <h4 class="font-semibold text-gray-900">Spanish</h4>
                  <p class="text-sm text-gray-600">Complete Spanish rubric and feedback</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Support -->
        <div class="text-center">
          <h2 class="text-2xl font-semibold text-gray-900 mb-4">🆘 Need More Help?</h2>
          <p class="text-gray-600">
            If you have questions or need assistance, please contact your system administrator.
          </p>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import Layout from '@/components/Layout.vue'
</script>
