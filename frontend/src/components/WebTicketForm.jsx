import React, { useState } from 'react';
import { 
  Box, 
  Button, 
  FormControl, 
  FormLabel, 
  Input, 
  Textarea, 
  Select, 
  VStack, 
  Heading, 
  useToast,
  Text,
  HStack,
  IconButton,
  Flex,
  Badge
} from '@chakra-ui/react';
import { DeleteIcon, AttachmentIcon } from '@chakra-ui/icons';
import axios from 'axios';

const WebTicketForm = () => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    email: '',
    name: '',
    location: '',
    asset_tag: '',
    priority: 'MEDIUM',
    category: ''
  });
  
  const [files, setFiles] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [ticketNumber, setTicketNumber] = useState(null);
  const toast = useToast();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleFileChange = (e) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      setFiles([...files, ...newFiles]);
    }
  };

  const removeFile = (index) => {
    const updatedFiles = [...files];
    updatedFiles.splice(index, 1);
    setFiles(updatedFiles);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      // Create form data for file upload
      const submitData = new FormData();
      
      // Add form fields
      Object.keys(formData).forEach(key => {
        if (formData[key]) {
          submitData.append(key, formData[key]);
        }
      });
      
      // Add files
      files.forEach(file => {
        submitData.append('files', file);
      });

      // Submit the form
      const response = await axios.post(
        '/api/tickets/web-form/with-attachments',
        submitData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      // Show success message
      toast({
        title: 'Ticket Created',
        description: `Your ticket #${response.data.ticket_number} has been created successfully.`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });

      // Reset form
      setFormData({
        title: '',
        description: '',
        email: '',
        name: '',
        location: '',
        asset_tag: '',
        priority: 'MEDIUM',
        category: ''
      });
      setFiles([]);
      setTicketNumber(response.data.ticket_number);
    } catch (error) {
      console.error('Error submitting ticket:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to create ticket. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Box p={6} borderWidth="1px" borderRadius="lg" boxShadow="md" bg="white">
      <Heading size="lg" mb={6}>Submit a Support Ticket</Heading>
      
      {ticketNumber ? (
        <Box mb={6} p={4} bg="green.50" borderRadius="md">
          <Text fontSize="lg">
            Your ticket <Badge colorScheme="green">{ticketNumber}</Badge> has been created successfully.
          </Text>
          <Button mt={4} colorScheme="blue" onClick={() => setTicketNumber(null)}>
            Submit Another Ticket
          </Button>
        </Box>
      ) : (
        <form onSubmit={handleSubmit}>
          <VStack spacing={4} align="stretch">
            <FormControl isRequired>
              <FormLabel>Title</FormLabel>
              <Input 
                name="title" 
                value={formData.title} 
                onChange={handleInputChange} 
                placeholder="Brief summary of the issue"
              />
            </FormControl>
            
            <FormControl isRequired>
              <FormLabel>Description</FormLabel>
              <Textarea 
                name="description" 
                value={formData.description} 
                onChange={handleInputChange} 
                placeholder="Please provide details about your issue"
                rows={5}
              />
            </FormControl>
            
            <HStack spacing={4}>
              <FormControl isRequired>
                <FormLabel>Your Name</FormLabel>
                <Input 
                  name="name" 
                  value={formData.name} 
                  onChange={handleInputChange} 
                  placeholder="Your full name"
                />
              </FormControl>
              
              <FormControl isRequired>
                <FormLabel>Email</FormLabel>
                <Input 
                  name="email" 
                  type="email" 
                  value={formData.email} 
                  onChange={handleInputChange} 
                  placeholder="Your email address"
                />
              </FormControl>
            </HStack>
            
            <HStack spacing={4}>
              <FormControl>
                <FormLabel>Location</FormLabel>
                <Input 
                  name="location" 
                  value={formData.location} 
                  onChange={handleInputChange} 
                  placeholder="Your office location"
                />
              </FormControl>
              
              <FormControl>
                <FormLabel>Asset Tag (if applicable)</FormLabel>
                <Input 
                  name="asset_tag" 
                  value={formData.asset_tag} 
                  onChange={handleInputChange} 
                  placeholder="Asset tag or ID"
                />
              </FormControl>
            </HStack>
            
            <HStack spacing={4}>
              <FormControl>
                <FormLabel>Priority</FormLabel>
                <Select name="priority" value={formData.priority} onChange={handleInputChange}>
                  <option value="LOW">Low</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="HIGH">High</option>
                  <option value="CRITICAL">Critical</option>
                </Select>
              </FormControl>
              
              <FormControl>
                <FormLabel>Category</FormLabel>
                <Select name="category" value={formData.category} onChange={handleInputChange}>
                  <option value="">-- Select Category --</option>
                  <option value="HARDWARE">Hardware</option>
                  <option value="SOFTWARE">Software</option>
                  <option value="NETWORK">Network</option>
                  <option value="EMAIL">Email</option>
                  <option value="ACCESS">Access/Permissions</option>
                  <option value="OTHER">Other</option>
                </Select>
              </FormControl>
            </HStack>
            
            <FormControl>
              <FormLabel>Attachments</FormLabel>
              <Input
                type="file"
                multiple
                onChange={handleFileChange}
                display="none"
                id="file-upload"
              />
              <Button
                leftIcon={<AttachmentIcon />}
                onClick={() => document.getElementById('file-upload').click()}
                colorScheme="gray"
                size="md"
              >
                Add Files
              </Button>
              
              {files.length > 0 && (
                <Box mt={2}>
                  <Text mb={2} fontWeight="medium">Attached Files:</Text>
                  <VStack align="stretch" spacing={2}>
                    {files.map((file, index) => (
                      <Flex key={index} p={2} bg="gray.50" borderRadius="md" alignItems="center">
                        <Text flex="1" isTruncated>{file.name}</Text>
                        <Text color="gray.500" fontSize="sm" mx={2}>
                          {(file.size / 1024).toFixed(0)} KB
                        </Text>
                        <IconButton
                          icon={<DeleteIcon />}
                          size="sm"
                          colorScheme="red"
                          variant="ghost"
                          onClick={() => removeFile(index)}
                          aria-label="Remove file"
                        />
                      </Flex>
                    ))}
                  </VStack>
                </Box>
              )}
            </FormControl>
            
            <Button 
              mt={6} 
              colorScheme="blue" 
              type="submit" 
              isLoading={isSubmitting}
              loadingText="Submitting"
              size="lg"
            >
              Submit Ticket
            </Button>
          </VStack>
        </form>
      )}
    </Box>
  );
};

export default WebTicketForm;