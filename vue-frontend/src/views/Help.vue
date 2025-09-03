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
              <li>Go to <strong>Text Input</strong> and paste your memo or business text</li>
              <li>Click <strong>Submit for Evaluation</strong> and wait for AI analysis</li>
              <li>View your <strong>Overall Feedback</strong> with scores and suggestions</li>
              <li>Review detailed <strong>Rubric Scores</strong> for specific improvements</li>
            </ol>
          </div>
        </div>

        <!-- Features Overview -->
        <div class="mb-12">
          <h2 class="text-2xl font-semibold text-gray-900 mb-4">✨ Key Features</h2>
          <div class="grid md:grid-cols-2 gap-6">
            <div class="bg-gray-50 rounded-lg p-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-3">📝 Text Input</h3>
              <p class="text-gray-600 mb-3">Submit any business memo, report, or professional text for evaluation.</p>
              <ul class="text-sm text-gray-600 space-y-1">
                <li>• Maximum 10,000 characters</li>
                <li>• Real-time character counter</li>
                <li>• Progress tracking during analysis</li>
              </ul>
            </div>
            <div class="bg-gray-50 rounded-lg p-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-3">📊 Overall Feedback</h3>
              <p class="text-gray-600 mb-3">Get comprehensive evaluation with overall score and detailed insights.</p>
              <ul class="text-sm text-gray-600 space-y-1">
                <li>• Overall score (1-5 scale)</li>
                <li>• Strengths identification</li>
                <li>• Improvement opportunities</li>
              </ul>
            </div>
            <div class="bg-gray-50 rounded-lg p-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-3">🎯 Rubric Scores</h3>
              <p class="text-gray-600 mb-3">Detailed breakdown of performance across multiple criteria.</p>
              <ul class="text-sm text-gray-600 space-y-1">
                <li>• Individual criterion scores</li>
                <li>• Specific justifications</li>
                <li>• Targeted improvement areas</li>
              </ul>
            </div>
            <div class="bg-gray-50 rounded-lg p-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-3">⚙️ Admin Features</h3>
              <p class="text-gray-600 mb-3">Configuration and system management for administrators.</p>
              <ul class="text-sm text-gray-600 space-y-1">
                <li>• Rubric configuration (integrated in prompt.yaml)</li>
                <li>• System settings</li>
                <li>• User management</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Evaluation Rubric -->
        <div class="mb-12">
          <h2 class="text-2xl font-semibold text-gray-900 mb-4">📋 Evaluation Rubric</h2>
          <div class="bg-green-50 rounded-lg p-6 mb-6">
            <p class="text-gray-700 mb-4">
              Your text is evaluated across multiple criteria, each scored on a 1-5 scale:
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
            <div class="border-l-4 border-blue-500 pl-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-2">📝 Content & Structure</h3>
              <p class="text-gray-600 mb-2">Evaluates the clarity, organization, and logical flow of your content.</p>
              <ul class="text-sm text-gray-600 space-y-1">
                <li>• Clear purpose and main message</li>
                <li>• Logical organization and flow</li>
                <li>• Appropriate length and scope</li>
                <li>• Effective use of headings and sections</li>
              </ul>
            </div>

            <div class="border-l-4 border-green-500 pl-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-2">💬 Clarity & Communication</h3>
              <p class="text-gray-600 mb-2">Assesses how well your message is communicated to the reader.</p>
              <ul class="text-sm text-gray-600 space-y-1">
                <li>• Clear and concise language</li>
                <li>• Appropriate tone and style</li>
                <li>• Effective use of examples and evidence</li>
                <li>• Audience-appropriate language</li>
              </ul>
            </div>

            <div class="border-l-4 border-purple-500 pl-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-2">🎯 Purpose & Impact</h3>
              <p class="text-gray-600 mb-2">Measures how effectively your text achieves its intended purpose.</p>
              <ul class="text-sm text-gray-600 space-y-1">
                <li>• Clear call-to-action or conclusion</li>
                <li>• Persuasive arguments and reasoning</li>
                <li>• Professional credibility and authority</li>
                <li>• Memorable and impactful messaging</li>
              </ul>
            </div>

            <div class="border-l-4 border-orange-500 pl-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-2">🔍 Technical Quality</h3>
              <p class="text-gray-600 mb-2">Reviews grammar, spelling, formatting, and technical accuracy.</p>
              <ul class="text-sm text-gray-600 space-y-1">
                <li>• Grammar and spelling accuracy</li>
                <li>• Proper formatting and presentation</li>
                <li>• Consistent style and terminology</li>
                <li>• Factual accuracy and reliability</li>
              </ul>
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
                <span><strong>Be specific:</strong> Include concrete details and examples to support your points</span>
              </li>
              <li class="flex items-start">
                <span class="text-yellow-600 mr-2 mt-1">•</span>
                <span><strong>Structure clearly:</strong> Use headings, bullet points, and logical organization</span>
              </li>
              <li class="flex items-start">
                <span class="text-yellow-600 mr-2 mt-1">•</span>
                <span><strong>Consider your audience:</strong> Use appropriate language and tone for your readers</span>
              </li>
              <li class="flex items-start">
                <span class="text-yellow-600 mr-2 mt-1">•</span>
                <span><strong>Review before submitting:</strong> Check for grammar, spelling, and clarity issues</span>
              </li>
              <li class="flex items-start">
                <span class="text-yellow-600 mr-2 mt-1">•</span>
                <span><strong>Focus on purpose:</strong> Ensure your text clearly achieves its intended goal</span>
              </li>
            </ul>
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
