<template>
  <div>
    <h1>{{ message }}</h1>
  </div>
</template>

<script>
import request from '@/utils/request'

export default {
  data() {
    return {
      message: ''
    }
  },
  async created() {
    try {
      const response = await request.get('/api/hello');
      this.message = response.data.message;
    } catch (error) {
      console.error('Failed to fetch data', error);
    }
  }
}
</script>