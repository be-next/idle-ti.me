# idle-ti.me website

![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/be-next/idle-ti.me?logo=github)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/be-next/idle-ti.me/publish.yml?label=build%20%26%20publish)

[idle-ti.me](https://idle-ti.me) website is crafted with [Zola](https://www.getzola.org) and enhanced by [tabi](https://welpo.github.io/tabi) theme.

## Deploying a Static Website with Zola, Amazon S3, and CloudFront

This guide outlines the steps required to deploy and serve a static website built with Zola using Amazon Web Services (AWS) infrastructure, specifically S3 for storage and CloudFront for content delivery.

### Official Documentation References

* AWS CloudFront Setup Guide: [Amazon CloudFront Distribution Documentation](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/getting-started-cloudfront-overview.html)
* Zola AWS Deployment Guide: [Zola AWS S3 Deployment Documentation](https://www.getzola.org/documentation/deployment/aws-s3/)

### Required Configuration Steps

#### 1. Website Navigation Configuration

**Issue**: Sub-pages don't automatically redirect to `index.html` when accessed directly.

**Solution**:

* Create a CloudFront function or implement Lambda@Edge
* Configure the function to handle routing requests to the appropriate `index.html` file
* This ensures proper navigation throughout the website's directory structure

#### 2. Error Handling Setup

**Issue**: Default 403 errors appear instead of custom 404 pages when accessing non-existent content.

**Solution**:

* Access CloudFront distribution settings
* Configure custom error responses
* Map 403/404 status codes to the `404.html` page
* Ensure proper error status codes are returned to maintain SEO best practices

#### 3. Cache Management Strategy

**Issue**: CloudFront caching prevents immediate visibility of S3 bucket content updates.

**Solutions**:

A. Implement Automated Cache Invalidation:

* Utilize Zola's provided GitHub Actions workflow
* Configure the workflow to trigger CloudFront cache invalidation after successful deployments
* This ensures content updates are immediately visible to users

B. Resource Versioning Implementation:

* Add version identifiers to resource URLs
* Enable granular cache control for specific resources
* Minimize full cache invalidation requirements
* Optimize content delivery performance

### Practical Implementation

For a detailed example of these configurations in action, refer to the blog post: [Zola: How to deploy a website using S3 Bucket and CloudFront](https://idle-ti.me/blog/zola-aws/)

This implementation guide demonstrates the practical application of the above configurations in a production environment.
