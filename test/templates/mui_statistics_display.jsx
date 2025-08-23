{stats ? (
            <Grid container spacing={3} sx={{ mt: 2 }}>
              <Grid item xs={12} sm={6} md={4}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Total Items
                  </Typography>
                  <Typography variant="h4">{stats.total_items || 0}</Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Login Count
                  </Typography>
                  <Typography variant="h4">{stats.login_count || 0}</Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Last Login
                  </Typography>
                  <Typography variant="body1">
                    {stats.last_login ? new Date(stats.last_login).toLocaleString() : 'N/A'}
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Account Age
                  </Typography>
                  <Typography variant="h4">{stats.account_age_days || 0} days</Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Email Verified
                  </Typography>
                  <Typography variant="body1">
                    {stats.email_verified ? '✅ Verified' : '❌ Not Verified'}
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Account Created
                  </Typography>
                  <Typography variant="body1">
                    {stats.account_created ? new Date(stats.account_created).toLocaleDateString() : 'N/A'}
                  </Typography>
                </Paper>
              </Grid>
            </Grid>
          ) : (