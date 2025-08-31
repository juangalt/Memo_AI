# Test: Collapse Functionality in Detailed Feedback

## Test Steps

1. **Start the application**:
   ```bash
   docker compose up -d
   ```

2. **Navigate to the application**:
   - Open browser to `http://localhost`
   - Login with any credentials (mock mode)

3. **Submit text for evaluation**:
   - Go to "Text Input" page
   - Submit a longer text (at least 100+ characters) to get multiple segments
   - Example text:
     ```
     Executive Summary: This investment opportunity shows strong potential for growth in the healthcare technology sector.
     
     Market Analysis: The market is growing at 15% annually with increasing demand for digital health solutions.
     
     Financial Projections: We project a 25% ROI over 3 years with conservative estimates.
     ```

4. **Navigate to Detailed Feedback**:
   - Click "Detailed Feedback" in the top menu
   - Verify you see multiple segments

5. **Test Collapse Functionality**:
   - **Initial State**: All segments should be collapsed (content hidden)
   - **Expand Test**: Click "Expand" on any segment
     - ✅ Segment content should appear
     - ✅ Button should change to "Collapse"
   - **Collapse Test**: Click "Collapse" on the same segment
     - ✅ Segment content should disappear
     - ✅ Button should change to "Expand"
   - **Multiple Segments**: Test expanding/collapsing different segments independently

6. **Verify Content**:
   - Each segment should show:
     - Original Text (quoted)
     - Analysis comment
     - Thought-provoking questions
     - Suggestions for improvement

## Expected Behavior

- ✅ Segments start collapsed by default
- ✅ Clicking "Expand" shows segment content
- ✅ Clicking "Collapse" hides segment content
- ✅ Button text changes appropriately
- ✅ Multiple segments can be expanded/collapsed independently
- ✅ All segment content displays correctly when expanded

## Troubleshooting

If collapse buttons still don't work:
1. Check browser console for JavaScript errors
2. Verify the Vue.js application is running correctly
3. Ensure the DetailedFeedback component is properly loaded
4. Check that the `expandedSegments` reactive state is working
