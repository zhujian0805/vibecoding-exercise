# 🚀 Create a Pull Request Page for React OAuth Webapp

I need you to create a new "Pull Request" page for an existing React TypeScript OAuth webapp that integrates with GitHub's API. The application follows a modular MVC architecture with proper separation of concerns.

## 📋 Requirements

**Create a complete Pull Request management page that includes:**

1. **Frontend Component** (`frontend/src/components/PullRequests.tsx`)
2. **Backend API Integration** (controller, service, model)
3. **Navigation Integration**
4. **Routing Setup**
5. **Styling** (following existing patterns)

## 🏗️ Architecture Patterns to Follow

**Frontend Structure:**
- Main component in `frontend/src/components/PullRequests.tsx`
- Modular sub-components in `frontend/src/components/pullrequests/` directory:
  - `PullRequestSearch.tsx` - Search functionality
  - `PullRequestControls.tsx` - Sort/filter controls
  - `PullRequestTableHeader.tsx` - Sortable table header
  - `PullRequestTableRow.tsx` - Individual PR row
  - `PullRequestPagination.tsx` - Pagination controls
  - `types.ts` - TypeScript interfaces
  - `utils.ts` - Utility functions
  - `index.ts` - Clean exports

**Backend Structure:**
- Model: `backend/models/pullrequest.py`
- Controller: `backend/controllers/pullrequest_controller.py` 
- Service: `backend/services/pullrequest_service.py`
- API endpoint: `/api/pullrequests`

## 📊 Data Structure

**Pull Request Interface:**
```typescript
interface PullRequest {
  id: number;
  number: number;
  title: string;
  body: string;
  state: 'open' | 'closed' | 'merged';
  user: {
    login: string;
    avatar_url: string;
    html_url: string;
  };
  created_at: string;
  updated_at: string;
  closed_at?: string;
  merged_at?: string;
  html_url: string;
  base: {
    ref: string;
    sha: string;
  };
  head: {
    ref: string;
    sha: string;
  };
  repository: {
    name: string;
    full_name: string;
    html_url: string;
  };
  draft: boolean;
  mergeable?: boolean;
  mergeable_state: string;
  merged_by?: {
    login: string;
    avatar_url: string;
  };
  additions: number;
  deletions: number;
  changed_files: number;
  comments: number;
  review_comments: number;
  commits: number;
}
```

## 🎯 Core Features

1. **List View:**
   - Display all pull requests (created, assigned, mentioned, review requested)
   - Tabbed interface for different PR types
   - State filtering (open, closed, merged, draft)
   - Repository filtering

2. **Search & Sort:**
   - Search by title, body, author, repository
   - Sort by: created, updated, popularity, activity, comments
   - Advanced filters: state, repository, author, labels

3. **Data Display:**
   - PR number, title, state badge
   - Author info with avatar
   - Repository name
   - Created/updated dates
   - Stats: comments, reviews, changes (+/- lines)
   - Branch information (base ← head)

4. **Actions:**
   - Open PR in GitHub
   - Copy PR URL
   - Quick state filtering

5. **Pagination:**
   - Items per page selection (10, 20, 30, 50, 100)
   - Smart page navigation
   - Results count display

## 🎨 UI Patterns to Follow

**Match existing component patterns:**
- Use same loading states (`<div className="loading">`)
- Error handling with retry button
- Search form with clear button
- Compact controls section
- Sortable table headers with icons
- State badges with appropriate colors
- Responsive design with proper mobile handling

**CSS Classes to Use:**
- `.pullrequests` - Main container
- `.pullrequests-header` - Header section
- `.search-form`, `.search-input` - Search components
- `.pullrequests-table` - Data table
- `.pagination` - Pagination controls
- `.state-badge` - PR state indicators
- `.pr-number`, `.pr-title` - PR identification
- `.author-info` - Author display
- `.branch-info` - Branch display

## 🔌 GitHub API Integration

**API Endpoints to Use:**
- `GET /user/issues?filter=all&state=all&pulls=true` - All PRs
- `GET /repos/{owner}/{repo}/pulls` - Repository PRs
- `GET /search/issues?q=author:{user}+type:pr` - Search PRs

**Authentication:**
- Use existing OAuth flow and session management
- Include `withCredentials: true` for API calls
- Handle rate limiting and errors gracefully

## 🧭 Navigation Integration

**Add to Navigation.tsx:**
```tsx
<li className={location.pathname === '/pullrequests' ? 'active' : ''}>
  <Link to="/pullrequests">Pull Requests</Link>
</li>
```

**Add to App.tsx Routes:**
```tsx
<Route 
  path="/pullrequests" 
  element={
    <ProtectedRoute isAuthenticated={authState.authenticated}>
      <PullRequests />
    </ProtectedRoute>
  } 
/>
```

**Add to HomePage.tsx features:**
```tsx
<Link to="/pullrequests" className="feature-card">
  <h3>Pull Requests</h3>
  <p>Manage your GitHub pull requests across all repositories.</p>
</Link>
```

## 💾 State Management

Follow existing patterns:
- Use `useState` for component state
- `useEffect` for data fetching
- `useCallback` for memoized functions
- Implement proper loading, error, and success states
- Cache API responses when appropriate

## 🎨 Styling Requirements

**Create modular CSS files:**
- `frontend/src/styles/pullrequests.css` - Main PR styles
- Include state-specific badge colors
- Responsive table design
- Hover effects and interactions
- Dark/light theme support

**State Badge Colors:**
- Open: Green (#28a745)
- Closed: Red (#dc3545)
- Merged: Purple (#6f42c1)
- Draft: Gray (#6c757d)

## 🔍 Advanced Features (Optional)

1. **Bulk Actions:** Select multiple PRs for batch operations
2. **Advanced Filtering:** Date ranges, label filtering, milestone filtering
3. **PR Preview:** Inline diff view or expandable details
4. **Notifications:** Mark as read/unread
5. **Assignment Management:** Assign reviewers

## 📱 Responsive Design

- Mobile-friendly table (consider card layout for small screens)
- Collapsible filters on mobile
- Touch-friendly pagination controls
- Optimized for both desktop and mobile viewing

## 🧪 Error Handling

- Network error recovery
- GitHub API rate limit handling
- Empty state messaging
- Loading skeletons
- Graceful degradation

## 📁 Expected File Structure After Implementation

```
frontend/src/components/
├── PullRequests.tsx
└── pullrequests/
    ├── PullRequestSearch.tsx
    ├── PullRequestControls.tsx
    ├── PullRequestTableHeader.tsx
    ├── PullRequestTableRow.tsx
    ├── PullRequestPagination.tsx
    ├── types.ts
    ├── utils.ts
    └── index.ts

backend/
├── models/pullrequest.py
├── controllers/pullrequest_controller.py
└── services/pullrequest_service.py

frontend/src/styles/
└── pullrequests.css
```

## 🎯 Implementation Notes

Please implement this following the exact same architectural patterns, code style, and component structure as the existing Repositories, Gists, Followers, and Following pages in the codebase.

Key implementation priorities:
1. **Consistency:** Match existing patterns exactly
2. **Modularity:** Break components into reusable pieces
3. **TypeScript:** Full type safety throughout
4. **Responsiveness:** Mobile-first design approach
5. **Performance:** Efficient API calls and caching
6. **Accessibility:** Proper ARIA labels and keyboard navigation
7. **Error Handling:** Comprehensive error states and recovery

## 🚀 Getting Started

1. Start with the backend model and service layer
2. Implement the controller and API endpoints
3. Create the main frontend component
4. Build modular sub-components
5. Add navigation and routing
6. Style with CSS following existing patterns
7. Test across different screen sizes and states
8. Optimize performance and add error handling

Remember to test the implementation thoroughly and ensure it integrates seamlessly with the existing OAuth flow and application architecture.
